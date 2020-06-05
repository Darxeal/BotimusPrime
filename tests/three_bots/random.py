from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
import math

PI = math.pi

BALL = BallState(
    physics=Physics(
        location=Vector3(0, 0, 93),
        velocity=Vector3(0, 0, 0),
        rotation=Rotator(0, 0, 0),
        angular_velocity=Vector3(0, 0, 0)
    )
)

CARS = {
    0: CarState(
        physics=Physics(
            location=Vector3(0, -4608, 20),
            velocity=Vector3(0, 0, 0),
            rotation=Rotator(0, PI/2, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    ),

    1: CarState(
        physics=Physics(
            location=Vector3(256, -3840, 20),
            velocity=Vector3(0, 0, 0),
            rotation=Rotator(0, PI/2, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    ),

    2: CarState(
        physics=Physics(
            location=Vector3(-2048, -2560, 20),
            velocity=Vector3(0, 0, 0),
            rotation=Rotator(0, PI/4, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    ),
}

GAME_STATE = GameState(
    ball=BALL,
    cars=CARS
)
