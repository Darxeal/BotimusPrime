from rlbottraining.training_exercise import Playlist
from training.shots import EasyShot


def make_default_playlist() -> Playlist:
    return [
        EasyShot()
    ]
