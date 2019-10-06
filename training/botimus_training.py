from pathlib import Path

from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.common_graders.goal_grader import StrikerGrader, Grader, GoalieGrader
from rlbottraining.rng import SeededRandomNumberGenerator

from rlutilities.simulation import Car, Ball
from rlutilities.linear_algebra import vec3, rotation_to_euler, mat3



def vec3_to_Vector3(vec: vec3) -> Vector3:
    return Vector3(vec[0], vec[1], vec[2])


def mat3_to_Rotator(mat: mat3) -> Rotator:
    pyr = rotation_to_euler(mat)
    return Rotator(pyr[0], pyr[1], pyr[2])


class BotimusExercise(TrainingExercise):
    
    def __init__(self, grader: Grader):

        excercise_name = str(self.__class__.__name__)
        super().__init__(excercise_name, grader)

        self.rng: SeededRandomNumberGenerator = None

        self.match_config.player_configs = [
            PlayerConfig.bot_config(
                Path(__file__).absolute().parent.parent / 'botimus.cfg', Team.BLUE
            )
        ]

    def make_game_state(self, rng: SeededRandomNumberGenerator):
        self.rng = rng
        ball = Ball()
        car = Car()
        self.set_car_ball_state(car, ball)
        return GameState(
            ball=BallState(
                physics=Physics(
                    location=vec3_to_Vector3(ball.position),
                    velocity=vec3_to_Vector3(ball.velocity),
                    angular_velocity=vec3_to_Vector3(ball.angular_velocity)
                )
            ),
            cars={
                0: CarState(
                    physics=Physics(
                        location=vec3_to_Vector3(car.position),
                        velocity=vec3_to_Vector3(car.velocity),
                        angular_velocity=vec3_to_Vector3(car.angular_velocity),
                        rotation=mat3_to_Rotator(car.orientation)
                    ),
                    boost_amount=car.boost
                )
            }
        )

    def set_car_ball_state(self, car: Car, ball: Ball):
        pass


class BotimusGoalieExcercise(BotimusExercise):

    timeout: float = 10

    def __init__(self):
        super().__init__(GoalieGrader(self.timeout))

class BotimusStrikerExcercise(BotimusExercise):

    timeout: float = 10

    def __init__(self):
        super().__init__(StrikerGrader(self.timeout))
