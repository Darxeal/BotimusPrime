from rlbottraining.training_exercise import Playlist
from training.shots import *
from training.tests import *


def make_default_playlist() -> Playlist:
    return [
        TurnAndTravelTest()
    ]
