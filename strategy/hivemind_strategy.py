from typing import List, Optional, Dict

from maneuvers.air.recovery import Recovery
from maneuvers.half_flip_pickup import HalfFlipPickup
from maneuvers.refuel import Refuel
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.strikes.clear_into_corner import ClearIntoCorner
from maneuvers.strikes.double_jump import DoubleJump
from rlutilities.simulation import Pad
from rlutilities.linear_algebra import vec3
from strategy.kickoffs import KickoffStrategy
from strategy.offense import Offense
from utils.drawing import DrawingTool
from utils.drone import Drone
from utils.game_info import GameInfo
from utils.intercept import Intercept
from utils.vector_math import align, ground, ground_distance, distance
from utils.arena import Arena


MIN_GOOD_ALIGN = 0.2

class HivemindStrategy:
    def __init__(self, info: GameInfo, logger):
        self.info: GameInfo = info
        self.logger = logger
        self.offense: Offense = Offense(info)

        # the drone that is currently committed to hitting the ball
        self.drone_going_for_ball: Optional[Drone] = None
        # drone that stays back near the goal
        self.drone_defending: Optional[Drone] = None

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
        our_goal = ground(info.my_goal.center)

        # drone finished its maneuver, no one is going for ball
        if self.drone_going_for_ball is not None and self.drone_going_for_ball.maneuver is None:
            self.drone_going_for_ball = None
        # drone finished its maneuver, no one is defending
        if self.drone_defending is not None and self.drone_defending.maneuver is None:
            self.drone_defending = None
        
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
        if unemployed_drones:
            self.defending_drone = min(unemployed_drones, key=lambda d: ground_distance(d.car, info.my_goal.center))	

        for drone in unemployed_drones:
            # TODO Better rotations
            shadow_distance = 7000 if drone is self.defending_drone else 3000
            drone.maneuver = ShadowDefense(self.defending_drone.car, info, info.ball.position, shadow_distance)

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

        else:
            # if no good shot, pick one closest to our goal
            best_intercept = min(our_intercepts, key=lambda i: ground_distance(i.car, our_goal))
            # find out which drone does the intercept belong to
            self.drone_going_for_ball = next(drone for drone in ready_drones if drone.car == best_intercept.car)
            # try to clear
            if 250 < best_intercept.ball.position[2] < 550:
                # taken out of ClearIntoCorner
                one_side = [vec3(Arena.size[0], Arena.size[1] * i/5, 0) for i in range(-5, 5)]
                other_side = [vec3(-p[0], p[1], 0) for p in one_side]
                target = ClearIntoCorner.pick_easiest_target(best_intercept.car, best_intercept.ball, one_side + other_side)
                self.drone_going_for_ball.maneuver = DoubleJump(best_intercept.car, info, target=target)
            self.drone_going_for_ball.maneuver = ClearIntoCorner(best_intercept.car, info)

        ready_drones.remove(self.drone_going_for_ball)

    def render(self, draw: DrawingTool):
        pass
