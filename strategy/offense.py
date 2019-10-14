from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_strike import GroundStrike
from maneuvers.strikes.wall_strike import WallStrike
from maneuvers.strikes.strike import Strike, Maneuver, ChainableManeuver
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.driving.travel import Travel
from maneuvers.chain_maneuver import ChainManeuver
from maneuvers.chainable.turn import Turn
from maneuvers.chainable.powerslide import Powerslide
from utils.game_info import GameInfo, Ball, Car, vec3
from typing import List

class Offense:

    @staticmethod
    def get_best_strike(car: Car, ball: Ball, target: vec3) -> ChainManeuver:
        copy = Ball(ball)

        stabilizers: List[ChainableManeuver] = [
            Turn(car), Powerslide(car)
        ]

        strikes: List[Strike] = [
            DodgeStrike(car, ball, target),
            GroundStrike(car, ball, target),
            WallStrike(car, ball, target),
        ]

        while copy.time < car.time + 20.0:
            for _ in range(5):
                dt = 1.0 / 120.0
                copy.step(dt)

            for strike in strikes:
                strike.configure(copy)
                if strike.is_intercept_desirable():
                    # for stabilizer in stabilizers:
                    #     stabilizer.target = strike.get_facing_target()
                    #     if stabilizer.viable():
                    #         better_car = stabilizer.simulate()
                    #         strike.car = better_car
                    #         strike.configure_mechanics()
                            # if strike.is_intercept_reachable():
                            #     return ChainManeuver(car, [stabilizer], strike)
                    if strike.is_intercept_reachable():
                        return strike

        print("Didn't find any possible Strike.")
            
