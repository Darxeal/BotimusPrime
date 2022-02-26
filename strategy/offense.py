from typing import Optional

from maneuvers.dribbling.carry_and_flick import CarryAndFlick
from maneuvers.general_defense import GeneralDefense
from maneuvers.maneuver import Maneuver
from maneuvers.strikes.aerial_strike import AerialStrike, FastAerialStrike
from maneuvers.strikes.close_shot import CloseShot
from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_strike import GroundStrike
from maneuvers.strikes.mirror_strike import MirrorStrike
from maneuvers.strikes.strike import Strike
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Car, Ball
from tools.game_info import GameInfo
from tools.vector_math import distance, ground_distance, align


def aerial_shot(info: GameInfo, car: Car, target: vec3) -> Optional[AerialStrike]:
    aerial_strikes = [
        # AirRollStrike(car, info, target),
        FastAerialStrike(car, info, target),
    ]

    strikes_i_have_enough_boost_for = [strike for strike in aerial_strikes if strike.boost_required() < car.boost]
    if not strikes_i_have_enough_boost_for:
        return None

    return min(strikes_i_have_enough_boost_for, key=lambda strike: strike.intercept.time)


def direct_shot(info: GameInfo, car: Car, target: vec3) -> Strike:
    dodge_shot = DodgeStrike(car, info, target)
    ground_shot = GroundStrike(car, info, target)
    aerial_strike = aerial_shot(info, car, target)

    if (
            aerial_strike is not None
            and aerial_strike.intercept.time < dodge_shot.intercept.time
            and abs(aerial_strike.intercept.position[1] - info.their_goal.center[1]) > 500
    ):
        return aerial_strike

    if (
            dodge_shot.intercept.time < ground_shot.intercept.time - 0.1
            or ground_distance(dodge_shot.intercept, target) < 2000
            or distance(ground_shot.intercept.velocity, car.velocity) < 500
            or is_opponent_close(info, 300)
    ):
        if (
                ground_distance(dodge_shot.intercept, target) < 4000
                and abs(dodge_shot.intercept.position.x) < 2000
        ):
            return CloseShot(car, info, target)
        return dodge_shot
    return ground_shot


def any_shot(info: GameInfo, car: Car, target: vec3, intercept: Ball, allow_dribble=False) -> Maneuver:
    if (
            allow_dribble
            and (intercept.position[2] > 100 or abs(intercept.velocity[2]) > 250 or distance(car, info.ball) < 300)
            and abs(intercept.velocity[2]) < 700
            and ground_distance(car, intercept) < 1500
            and ground_distance(intercept, info.my_goal.center) > 1000
            and ground_distance(intercept, info.their_goal.center) > 1000
            and not is_opponent_close(info, info.ball.position[2] * 2 + 1000)
    ):
        return CarryAndFlick(car, info, target)

    direct = direct_shot(info, car, target)

    if not isinstance(direct, GroundStrike) and intercept.time < car.time + 4.0:
        alignment = align(car.position, intercept, target)
        if alignment < 0:
            if alignment < -0.3 or abs(intercept.position.y - target.y) < 3000:
                # Announcer.announce("[Strategy] Alignment is so bad I'll rather clear this")
                # return defense.any_clear(info, car)
                return GeneralDefense(car, info, intercept.position, 3000, force_nearest=True)
            return MirrorStrike(car, info, target)

    return direct


def is_opponent_close(info: GameInfo, dist: float) -> bool:
    for opponent in info.get_opponents():
        if ground_distance(opponent.position + opponent.velocity * 0.5, info.ball) < dist:
            return True
    return False
