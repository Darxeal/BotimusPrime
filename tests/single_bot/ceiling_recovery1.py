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
            location=Vector3(-2000, -3000, 500),
            velocity=Vector3(100, 100, 2300),
            rotation=Rotator(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
}

GAME_STATE = GameState(
    ball=BALL,
    cars=CARS
)
