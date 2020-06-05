from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator

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
            location=Vector3(-2000, -2000, 500),
            velocity=Vector3(500, 1000, 2300),
            rotation=Rotator(0, 0, 0),
            angular_velocity=Vector3(-1, 1, 2)
        )
    )
}

GAME_STATE = GameState(
    ball=BALL,
    cars=CARS
)
