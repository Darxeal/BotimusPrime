from math import pi, copysign
from dataclasses import dataclass

from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator

from rlbottraining.common_exercises.common_base_exercises import StrikerExercise
from rlbottraining.common_graders.goal_grader import StrikerGrader, Grader
from rlbottraining.rng import SeededRandomNumberGenerator

timeout = 20

@dataclass
class WallShot2(StrikerExercise):

    grader: Grader = StrikerGrader(timeout_seconds=5)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_state = BallState(Physics(
            location=Vector3(-2000, 0, 93),
            velocity=Vector3(3000, 10, 200)
        ))
        car_state = CarState(
            boost_amount=100,
            physics=Physics(
                location=Vector3(2000, -2000, 25),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, pi * rng.n11(), 0)
            )
        )

        game_state = GameState(ball=ball_state, cars={0: car_state})
        return game_state


@dataclass
class WallShot(StrikerExercise):

    grader: Grader = StrikerGrader(timeout_seconds=timeout)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_state = BallState(Physics(
            location=Vector3(1000, 0, 93),
            velocity=Vector3(rng.uniform(2500, 3000), 500 * rng.n11(), 50)
        ))
        car_state = CarState(
            boost_amount=100,
            physics=Physics(
                location=Vector3(2000, -2000, 25),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, pi * rng.n11(), 0)
            )
        )

        game_state = GameState(ball=ball_state, cars={0: car_state})
        return game_state

@dataclass
class CenteredShot(StrikerExercise):

    grader: Grader = StrikerGrader(timeout_seconds=timeout)

    ball_vel_z: float = 0

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_state = BallState(Physics(
            location=Vector3(1000 * rng.n11(), 2000, 93),
            velocity=Vector3(1000 * rng.n11(), 1000 * rng.n11(), self.ball_vel_z)
        ))
        car_state = CarState(
            boost_amount=100,
            physics=Physics(
                location=Vector3(2000, -2000, 25),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, pi * rng.n11(), 0)
            )
        )

        game_state = GameState(ball=ball_state, cars={0: car_state})
        return game_state

@dataclass
class AerialShot(StrikerExercise):

    grader: Grader = StrikerGrader(timeout_seconds=timeout)

    ball_vel_z: float = 0

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_state = BallState(Physics(
            location=Vector3(500 * rng.n11(), 2000, 93),
            velocity=Vector3(500 * rng.n11(), 500 * rng.n11(), 1500)
        ))
        car_state = CarState(
            boost_amount=100, jumped=False, double_jumped=False,
            physics=Physics(
                location=Vector3(1000 * rng.n11(), -1000, 25),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, pi * rng.n11(), 0)
            )
        )

        game_state = GameState(ball=ball_state, cars={0: car_state})
        return game_state

@dataclass
class Dribbling(StrikerExercise):

    grader: Grader = StrikerGrader(timeout_seconds=timeout)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_state = BallState(Physics(
            location=Vector3(500 * rng.n11(), -1000, 500),
            velocity=Vector3(500 * rng.n11(), 500 * rng.n11(), 500)
        ))
        car_state = CarState(
            boost_amount=100, jumped=False, double_jumped=False,
            physics=Physics(
                location=Vector3(1000 * rng.n11(), -1000, 25),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, pi * rng.n11(), 0)
            )
        )

        game_state = GameState(ball=ball_state, cars={0: car_state})
        return game_state


@dataclass
class MirrorShot(StrikerExercise):

    grader: Grader = StrikerGrader(timeout_seconds=timeout)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        side = copysign(1, rng.n11())
        ball_state = BallState(Physics(
            location=Vector3(2000 * side, -1500, 93),
            velocity=Vector3(100 * rng.n11(), 700 * rng.n11(), 0)
        ))
        car_state = CarState(
            boost_amount=100,
            physics=Physics(
                location=Vector3(-2000 * side, -2000, 25),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, pi * rng.n11(), 0)
            )
        )

        game_state = GameState(ball=ball_state, cars={0: car_state})
        return game_state


@dataclass
class CornerShot(StrikerExercise):

    grader: Grader = StrikerGrader(timeout_seconds=timeout)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        side = copysign(1, rng.n11())
        ball_state = BallState(Physics(
            location=Vector3(3000 * side, 2000, 93),
            velocity=Vector3(100 * rng.n11(), 500 * rng.n11(), 0)
        ))
        car_state = CarState(
            boost_amount=100,
            physics=Physics(
                location=Vector3(-3000 * side, -2000, 25),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, pi * rng.n11(), 0)
            )
        )

        game_state = GameState(ball=ball_state, cars={0: car_state})
        return game_state
