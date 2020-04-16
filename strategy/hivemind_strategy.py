from typing import List, Optional, Dict

from maneuvers.air.recovery import Recovery
from maneuvers.half_flip_pickup import HalfFlipPickup
from maneuvers.refuel import Refuel
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.strikes.clear_into_corner import ClearIntoCorner
from maneuvers.driving.arrive import Arrive
from rlutilities.simulation import Pad
from rlutilities.linear_algebra import dot
from strategy.kickoffs import KickoffStrategy
from strategy.offense import Offense
from utils.drawing import DrawingTool
from utils.drone import Drone
from utils.game_info import GameInfo
from utils.intercept import Intercept
from utils.vector_math import align, ground, ground_distance, distance, ground_direction
from utils.arena import Arena


MIN_GOOD_ALIGN = 0.5
MIN_PASS_ALIGN = 0.3
PASS_ESTIMATED_BALL_SPEED = 1000

class HivemindStrategy:
    def __init__(self, info: GameInfo, logger):
        self.info: GameInfo = info
        self.logger = logger
        self.offense: Offense = Offense(info)

        # the drone that is currently committed to hitting the ball
        self.drone_going_for_ball: Optional[Drone] = None

        self.boost_reservations: Dict[Drone, Pad] = {}

    def set_kickoff_maneuvers(self, drones: List[Drone]):
        nearest_drone = min(drones, key=lambda drone: ground_distance(drone.car, self.info.ball))
        nearest_drone.maneuver = KickoffStrategy.choose_kickoff(self.info, nearest_drone.car)
        self.drone_going_for_ball = nearest_drone

        self.boost_reservations.clear()
        corner_drones = [drone for drone in drones if abs(drone.car.position[0]) > 2000]
        if len(corner_drones) > 1:
            other_corner_drone = next(drone for drone in corner_drones if drone is not nearest_drone)
            nearest_pad = min(self.info.large_boost_pads, key=lambda pad: distance(other_corner_drone.car, pad))
            other_corner_drone.maneuver = HalfFlipPickup(other_corner_drone.car, nearest_pad)
            self.boost_reservations[other_corner_drone] = nearest_pad

        for drone in drones:
            if drone is not nearest_drone and drone not in corner_drones:
                reserved_pads = {self.boost_reservations[d] for d in self.boost_reservations}
                drone.maneuver = Refuel(drone.car, self.info, self.info.my_goal.center, forbidden_pads=reserved_pads)
                self.boost_reservations[drone] = drone.maneuver.pad

    def set_maneuvers(self, drones: List[Drone]):
        info = self.info

        # drone finished its maneuver, no one is going for ball
        if self.drone_going_for_ball is not None and self.drone_going_for_ball.maneuver is None:
            self.drone_going_for_ball = None
        
        ready_drones = [drone for drone in drones if not drone.car.demolished
                            and (drone.maneuver is None or drone.maneuver.interruptible()) 
                            and drone != self.drone_going_for_ball]

        # recovery
        for drone in ready_drones:
            if not drone.car.on_ground:
                drone.maneuver = Recovery(drone.car)
                ready_drones.remove(drone)

        # all drones busy and cannot be interrupted
        if not ready_drones:
            return

        # decide which drone is going to commit
        if self.drone_going_for_ball is None:
            self.find_drone_going_for_ball(ready_drones)

        # we ran out of available drones
        if not ready_drones:
            return

        # clear expired boost reservations
        for drone in drones:
            if not isinstance(drone.maneuver, Refuel) and drone in self.boost_reservations:
                del self.boost_reservations[drone]

        # drones that need boost go for boost
        for drone in ready_drones:
            if drone.car.boost < 40:
                reserved_pads = {self.boost_reservations[drone] for drone in self.boost_reservations}
                drone.maneuver = Refuel(drone.car, info, info.ball.position, forbidden_pads=reserved_pads)
                if drone.maneuver.pad is None:
                    # TODO what happens if no boost pad is free?
                    self.logger.warn("No pad available!")
                self.boost_reservations[drone] = drone.maneuver.pad  # reserve chosen boost pad

        # all without maneuver go into defence
        unemployed_drones = [drone for drone in drones if drone.maneuver is None]
        for drone in unemployed_drones:
            # TODO Reposition
            shadow_distance = 7000 # 3000 for defending
            drone.maneuver = ShadowDefense(drone.car, info, info.ball.position, shadow_distance)

    def find_drone_going_for_ball(self, ready_drones: List[Drone]):
        info = self.info
        their_goal = ground(info.their_goal.center)
        our_goal = ground(info.my_goal.center)

        info.predict_ball()
        # estimate intercepts for all ready drones
        our_intercepts = [Intercept(drone.car, info.ball_predictions) for drone in ready_drones]
        # filter out bad intercepts
        good_intercepts = [i for i in our_intercepts if align(i.car.position, i.ball, their_goal) > MIN_GOOD_ALIGN or ground_distance(i.position, our_goal) > 6000]

        # good shot is possible
        if good_intercepts:
            # fastest good intercept
            best_intercept = min(good_intercepts, key=lambda intercept: intercept.time)
            # find out which drone does the intercept belong to
            self.drone_going_for_ball = next(drone for drone in ready_drones if drone.car == best_intercept.car)
            # take a shot
            self.drone_going_for_ball.maneuver = self.offense.any_shot(best_intercept.car, their_goal, best_intercept)
            ready_drones.remove(self.drone_going_for_ball)
            return

        # consider passing
        # FIXME passes suck right now. Maybe the receiving drone should also be locked in? Custom maneuver?
        if len(ready_drones) > 1:
            # find the fastest pass with decent alignment
            for intercept in sorted(our_intercepts, key=lambda i: i.time):
                drone_to_ball = ground_direction(intercept.car.position, intercept.ball)
                other_drones = [drone for drone in ready_drones if drone.car != intercept.car]
                # using linear prediction
                predicted_positions = [Arena.clamp(drone.car.position + drone.car.velocity * (intercept.time - info.time)) for drone in other_drones]
                ball_to_drones = [ground_direction(intercept.ball, pos) for pos in predicted_positions]
                alignments = [dot(drone_to_ball, ball_to_drone) for ball_to_drone in ball_to_drones]
                good_passes = [(drone, alignment) for drone, alignment in zip(other_drones, alignments) if alignment > MIN_PASS_ALIGN]

                # since intercepts are sorted, take first one with good passes
                if good_passes:
                    self.logger.debug("GOING FOR A PASS!")

                    receiving_drone = max(good_passes, key=lambda tup: tup[1])[0]

                    # find pass location and time
                    pass_location = ground((Arena.clamp(receiving_drone.car.position + receiving_drone.car.velocity * intercept.time) + their_goal) / 2)
                    pass_time = (intercept.time - info.time) + ground_distance(pass_location, intercept.ball) / PASS_ESTIMATED_BALL_SPEED

                    # make receiving drone drive to location
                    receiving_drone.maneuver = Arrive(receiving_drone.car)
                    receiving_drone.maneuver.target_direction = ground_direction(receiving_drone.car.position, their_goal)
                    receiving_drone.maneuver.target = pass_location
                    receiving_drone.maneuver.arrival_time = pass_time

                    # hit towards the pass location
                    self.drone_going_for_ball = next(drone for drone in ready_drones if drone.car == intercept.car)
                    self.drone_going_for_ball.maneuver = self.offense.any_shot(intercept.car, pass_location, intercept)

                    # remove from ready drones
                    ready_drones.remove(self.drone_going_for_ball)
                    ready_drones.remove(receiving_drone)
                    return

        # if no pass, just pick closest
        best_intercept = min(our_intercepts, key=lambda i: ground_distance(i.car, our_goal))
        # find out which drone does the intercept belong to
        self.drone_going_for_ball = next(drone for drone in ready_drones if drone.car == best_intercept.car)
        # try to clear
        self.drone_going_for_ball.maneuver = ClearIntoCorner(best_intercept.car, info)
        ready_drones.remove(self.drone_going_for_ball)

    def render(self, draw: DrawingTool):
        pass
