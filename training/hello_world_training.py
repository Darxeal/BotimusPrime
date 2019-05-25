from pathlib import Path
from math import pi, copysign
from dataclasses import dataclass

from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator

from rlbottraining.common_exercises.common_base_exercises import StrikerExercise, GoalieExercise
from rlbottraining.common_graders.goal_grader import StrikerGrader, Grader
from rlbottraining.rng import SeededRandomNumberGenerator


from striker import *

@dataclass
class AerialSave(GoalieExercise):

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(rng.uniform(-840, 840), -1500, 700),
                velocity=Vector3(0, -2000, 500),
            )),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, -5300, 0),
                        rotation=Rotator(0, pi / 2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                    jumped=False,
                    double_jumped=False,
                    boost_amount=100)
            }
        )



def inject_botimus_into_exercises(exercises):
    for exercise in exercises:
        exercise.match_config.player_configs = [
            PlayerConfig.bot_config(
                Path(__file__).absolute().parent.parent / 'botimus.cfg', Team.BLUE
            )
        ]

def make_default_playlist():
    exercises = [
        WallShot("wall"),
        WallShot2("wall2"),
        Dribbling("dribbling"),
        CenteredShot("rolling"),
        CenteredShot("bouncy", ball_vel_z=700),
        CornerShot("corner shot"),
        MirrorShot("mirror shot"),
        AerialShot("aerial")
    ]


    inject_botimus_into_exercises(exercises)

    return exercises
