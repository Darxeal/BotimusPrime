from typing import List, Optional

from maneuvers.air.recovery import Recovery
from maneuvers.driving.stop import Stop
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.refuel import Refuel
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.strikes.clear_into_corner import ClearIntoCorner
from maneuvers.strikes.strike import Strike
from rlutilities.simulation import Car
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

        self.drone_going_for_ball: Optional[Drone] = None

    def set_maneuvers(self, drones: List[Drone]):
        info = self.info
        their_goal = ground(info.their_goal.center)

        if self.drone_going_for_ball and self.drone_going_for_ball.maneuver is None:
            self.drone_going_for_ball = None

        for drone in drones:
            if drone.maneuver is None and not drone.car.on_ground:
                drone.maneuver = Recovery(drone.car)

        if self.drone_going_for_ball is None:
            ready_drones = [drone for drone in drones if drone.car.on_ground and not drone.controls.jump]
            if not ready_drones:
                return

            info.predict_ball()
            our_intercepts = [Intercept(drone.car, info.ball_predictions) for drone in ready_drones]
            good_intercepts = [i for i in our_intercepts if align(i.car.position, i.ball, their_goal) > 0.0]

            if not good_intercepts:
                good_intercepts = our_intercepts

            best_intercept = min(good_intercepts, key=lambda intercept: intercept.time)
            self.drone_going_for_ball = next(drone for drone in ready_drones if drone.car == best_intercept.car)

            if info.kickoff_pause:
                strike = Kickoff(best_intercept.car, info)
            elif align(best_intercept.car.position, best_intercept.ball, their_goal) > -0.2:
                strike = self.offense.any_shot(best_intercept.car, their_goal, best_intercept)
            else:
                strike = ClearIntoCorner(best_intercept.car, info)

            self.drone_going_for_ball.maneuver = strike

        for drone in drones:
            if drone.maneuver is None:
                if drone.car.boost < 40:
                    drone.maneuver = Refuel(drone.car, info, info.ball.position)
                else:
                    drone.maneuver = ShadowDefense(drone.car, info, info.ball.position, 4000)
