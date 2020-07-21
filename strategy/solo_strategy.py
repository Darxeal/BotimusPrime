from typing import List

from maneuvers.driving.stop import Stop
from maneuvers.general_defense import GeneralDefense
from maneuvers.recovery import Recovery
from maneuvers.refuel import Refuel
from maneuvers.strikes.strike import Strike
from rlutilities.simulation import Car
from strategy import offense, defense, kickoffs
from tools.arena import Arena
from tools.game_info import GameInfo
from tools.intercept import Intercept, estimate_time
from tools.vector_math import align, ground, ground_distance, distance


def best_intercept(info: GameInfo, cars: List[Car]) -> Intercept:
    if not cars:
        return Intercept(Car(), info.ball_predictions)
    intercepts = [Intercept(car, info.ball_predictions) for car in cars]
    return min(intercepts, key=lambda intercept: intercept.time)


def choose_maneuver(info: GameInfo, car: Car):
    info = info
    ball = info.ball

    opponents = info.get_opponents(car)

    their_goal = ground(info.their_goal.center)
    my_goal = ground(info.my_goal.center)

    my_hit = Intercept(car, info.ball_predictions)
    their_best_hit = best_intercept(info, opponents)
    opponent = their_best_hit.car

    # recovery
    if not car.on_ground:
        return Recovery(car)

    # kickoff
    if ball.position[0] == 0 and ball.position[1] == 0:
        return kickoffs.choose_kickoff(info, car)

    # don't save our own shots
    if info.about_to_score:
        if info.time_of_goal < their_best_hit.time - 2:
            return Stop(car)

    # save
    if info.about_to_be_scored_on:

        if align(car.position, my_hit.ball, their_goal) > 0.0:

            return offense.direct_shot(info, car, their_goal)

        return defense.any_clear(info, car)

    # fallback
    if align(car.position, my_hit.ball, my_goal) > 0.2:
        if (
            ground_distance(my_hit, my_goal) < 4000
            and abs(car.position[1]) < abs(my_hit.position[1])
        ):
            return defense.any_clear(info, car)
        return GeneralDefense(car, info, my_hit.ground_pos, 6000)

    # clear
    if (
        ground_distance(my_hit, my_goal) < 3500
        and abs(my_hit.position[0]) < 3000
        and ground_distance(car, my_goal) < 2500
    ):
        if align(car.position, my_hit.ball, their_goal) > 0:
            return offense.direct_shot(info, car, their_goal)
        return defense.any_clear(info, car)

    if distance(their_best_hit, their_goal) < distance(their_best_hit, my_goal):
        opponents_align = -align(opponent.position, their_best_hit.ball, their_goal)
    else:
        opponents_align = align(opponent.position, their_best_hit.ball, my_goal)

    # I can get to ball faster than them
    if my_hit.time < their_best_hit.time - 0.8:
        strike = offense.any_shot(info, car, their_goal, my_hit, allow_dribble=True)

        if not isinstance(strike, Strike):
            return strike

        if strike.intercept.time < their_best_hit.time - 0.8 \
        and (not info.about_to_score or strike.intercept.time < info.time_of_goal - 1):

            if strike.intercept.time - car.time > 4 and car.boost < 30 \
            and distance(strike.intercept.ground_pos, their_goal) > 3000 and distance(their_best_hit.ground_pos, my_goal) > 5000:

                return Refuel(car, info, my_hit.ground_pos)

            if abs(strike.intercept.ground_pos[0]) > Arena.size[0] - 800 and car.boost < 30:

                return Refuel(car, info, my_hit.ground_pos)

            if abs(strike.intercept.ball.position[1] - their_goal[1]) > 300 or ground_distance(strike.intercept, their_goal) < 900:
                return strike

    # they are out of position
    if (
        opponents_align < -0.1
        and my_hit.time < their_best_hit.time - opponents_align * 1.5
    ):

        strike = offense.any_shot(info, car, their_goal, my_hit, allow_dribble=True)

        if not isinstance(strike, Strike) or strike.intercept.is_viable \
        and (not info.about_to_score or strike.intercept.time < info.time_of_goal - 0.5):

            if (
                car.boost < 40
                and (distance(my_hit, their_goal) > 5000 or abs(my_hit.position[0]) > Arena.size[0] - 1500)
                and distance(opponent, their_best_hit) > 3000
            ):
                return Refuel(car, info, my_hit.ground_pos)

            if not isinstance(strike, Strike) or abs(strike.intercept.ball.position[1] - their_goal[1]) > 300 or ground_distance(strike.intercept, their_goal) < 900:
                return strike

        if distance(their_best_hit.ball, my_goal) > 7000 and \
            (distance(their_best_hit, opponent) > 3000 or align(opponent.position, their_best_hit.ball, my_goal) < 0) and car.boost < 30:
            return Refuel(car, info, my_hit.ground_pos)

        if car.boost < 35 and distance(their_best_hit, opponent) > 3000:
            refuel = Refuel(car, info, my_hit.ground_pos)
            if estimate_time(car, refuel.pad.position, 1400) < 1.5:
                return refuel

        if opponents_align < 0:
            return offense.any_shot(info, car, their_goal, my_hit, allow_dribble=True)

    shadow_distance = 4000 + opponents_align * 1500
    shadow_distance = max(shadow_distance, 3000)
    return GeneralDefense(car, info, their_best_hit.ground_pos, shadow_distance)
