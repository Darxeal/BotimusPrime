from typing import List, Optional, Dict

from maneuvers.air.recovery import Recovery
from maneuvers.driving.stop import Stop
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.refuel import Refuel
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.strikes.clear_into_corner import ClearIntoCorner
from maneuvers.strikes.strike import Strike
from rlutilities.simulation import Car, Pad
from strategy.offense import Offense
from utils.arena import Arena
from utils.drawing import DrawingTool
from utils.drone import Drone
from utils.game_info import GameInfo
from utils.intercept import Intercept, estimate_time
from utils.vector_math import align, ground, ground_distance, distance


class HivemindStrategy:
    def __init__(self, info: GameInfo):
        self.info: GameInfo = info
        self.offense: Offense = Offense(info)

        # the drone that is currently committed to hitting the ball
        self.drone_going_for_ball: Optional[Drone] = None

        self.boost_reservations: Dict[Drone, Pad] = {}

    def set_maneuvers(self, drones: List[Drone]):
        info = self.info
        their_goal = ground(info.their_goal.center)

        if self.drone_going_for_ball is not None and self.drone_going_for_ball.maneuver is None:
            self.drone_going_for_ball = None

        # recovery
        for drone in drones:
            if drone.maneuver is None and not drone.car.on_ground:
                drone.maneuver = Recovery(drone.car)

        # decide which drone is gonna commit
        if self.drone_going_for_ball is None:
            ready_drones = [drone for drone in drones if drone.car.on_ground and not drone.controls.jump]
            if not ready_drones:
                return

            info.predict_ball()
            our_intercepts = [Intercept(drone.car, info.ball_predictions) for drone in ready_drones]
            good_intercepts = [i for i in our_intercepts if align(i.car.position, i.ball, their_goal) > 0.0]

            if good_intercepts:
                best_intercept = min(good_intercepts, key=lambda intercept: intercept.time)
            else:
                best_intercept = max(our_intercepts, key=lambda i: align(i.car.position, i.ball, their_goal))

            # find out which drone does the intercept belong to
            self.drone_going_for_ball = next(drone for drone in ready_drones if drone.car == best_intercept.car)

            if info.kickoff_pause:
                strike = Kickoff(best_intercept.car, info)

            # if not completely out of position, go for a shot
            elif align(best_intercept.car.position, best_intercept.ball, their_goal) > -0.3:
                strike = self.offense.any_shot(best_intercept.car, their_goal, best_intercept)

            else:  # otherwise try to clear
                strike = ClearIntoCorner(best_intercept.car, info)

            self.drone_going_for_ball.maneuver = strike

        # clear expired boost reservations
        for drone in drones:
            if not isinstance(drone.maneuver, Refuel) and drone in self.boost_reservations:
                del self.boost_reservations[drone]

        for drone in drones:
            if drone.maneuver is None:
                if drone.car.boost < 40:
                    reserved_pads = {self.boost_reservations[drone] for drone in self.boost_reservations}
                    drone.maneuver = Refuel(drone.car, info, info.ball.position, forbidden_pads=reserved_pads)
                    self.boost_reservations[drone] = drone.maneuver.pad  # reserve chosen boost pad
                else:
                    drone.maneuver = ShadowDefense(drone.car, info, info.ball.position, 5000)

    def render(self, draw: DrawingTool):
        if self.drone_going_for_ball:
            draw.color(draw.orange)
            draw.line(self.drone_going_for_ball.car.position, self.info.ball.position)

        for drone in self.boost_reservations:
            draw.color(draw.pink)
            pad = self.boost_reservations[drone]
            draw.line(drone.car.position, pad.position)