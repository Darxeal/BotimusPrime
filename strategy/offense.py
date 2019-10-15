from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_strike import GroundStrike
from maneuvers.strikes.wall_strike import WallStrike
from maneuvers.strikes.shots import GroundShot, DodgeShot
from maneuvers.strikes.strike import Strike, Maneuver, ChainableManeuver
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.driving.travel import Travel
from maneuvers.chain_maneuver import ChainManeuver
from maneuvers.chainable.turn import Turn
from maneuvers.chainable.powerslide import Powerslide
from maneuvers.kit import *
from typing import List

class Offense:

    @staticmethod
    def makes_sense(car: Car, ball: Ball, target_goal: Goal) -> ChainManeuver:
        # return (
        #     abs(ball.position[1]) < abs(target_goal.center[1]) - 1500
        #     or abs(ball.position[0]) < target_goal.WIDTH / 2 + abs(ball.position[1] - target_goal.center[1]) - 300
        # )
        if ground_distance(ball, target_goal.center) > 3000:
            return True
        return dot(ground_direction(car, ball), ground_direction(ball, target_goal.center)) > 0


    @staticmethod
    def get_best_strike(car: Car, ball: Ball, target_goal: Goal) -> ChainManeuver:
        print("Offense - choosing best Strike")
        copy = Ball(ball)

        # stabilizers: List[ChainableManeuver] = [
        #     Turn(car),
        #     Powerslide(car)
        # ]

        strikes: List[Strike] = [
            WallStrike(car, ball),
            GroundShot(car, ball, target_goal),
            DodgeShot(car, ball, target_goal),
        ]

        earliest_time = 0

        while copy.time < car.time + 20.0:
            for _ in range(5):
                dt = 1.0 / 120.0
                copy.step(dt)

            if not Offense.makes_sense(car, copy, target_goal):
                earliest_time = copy.time
                continue

            for strike in strikes:
                strike.configure(copy)
                if strike.is_intercept_desirable():
                    # for stabilizer in stabilizers:
                    #     stabilizer.target = strike.get_facing_target()
                    #     if stabilizer.viable():
                    #         better_car = stabilizer.simulate()
                    #         strike.car = better_car
                    #         strike.configure_mechanics()
                    #         if strike.is_intercept_reachable():
                    #             return ChainManeuver(car, [stabilizer], strike)
                    if strike.is_intercept_reachable():
                        strike.earliest_intercept_time = earliest_time
                        return strike

        print("Didn't find any possible Strike.")
        return None
            
