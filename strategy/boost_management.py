from typing import Optional, Set

from rlutilities.linear_algebra import dot
from rlutilities.simulation import Car, BoostPad
from tools.game_info import GameInfo
from tools.intercept import pad_available_in_time
from tools.vector_math import distance, ground_direction, ground_distance


def choose_boostpad_to_pickup(info: GameInfo, car: Car, forbidden_pads: Set[BoostPad] = None) -> Optional[BoostPad]:
    if forbidden_pads is None:
        forbidden_pads = set()

    # consider pads which are available or going to spawn before we can reach them
    # active_pads = {pad for pad in info.large_boost_pads if pad_available_in_time(pad, car)}

    valid_pads = set(info.large_boost_pads) - forbidden_pads
    if not valid_pads:
        return None

    # a good candidate should be somewhere between us, our goal, and the ball
    # the easiest way to do that is to just take a weighted average of those positions
    pos = (info.ball.position + car.position * 2 + info.my_goal.center) / 4

    # and pick the closest valid pad to that position
    best_pad = min(valid_pads, key=lambda pad: distance(pad.position, pos))
    return best_pad if pad_available_in_time(best_pad, car) else None


def best_pad_on_the_way_to_ball(car: Car, info: GameInfo) -> Optional[BoostPad]:
    ball_to_goal = ground_direction(info.ball, info.their_goal.center)
    boosts_before_ball = [pad for pad in info.large_boost_pads if
                          dot(ball_to_goal, ground_direction(pad, info.ball)) > 0]
    if not boosts_before_ball:
        return None
    best_pad = min(boosts_before_ball, key=lambda pad: ground_distance(car, pad) + ground_distance(pad, info.ball))
    if not pad_available_in_time(best_pad, car):
        return None
    return best_pad


def best_pad_on_the_way_to_my_goal(car: Car, info: GameInfo) -> Optional[BoostPad]:
    best_pad = min(info.large_boost_pads,
                   key=lambda pad: ground_distance(car, pad) + ground_distance(pad, info.my_goal.center))
    if not pad_available_in_time(best_pad, car):
        return None
    return best_pad
