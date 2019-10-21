from rlbottraining.common_exercises.kickoff_exercise import KickoffExercise, Spawns, Playlist
from pathlib import Path

from rlbot.matchconfig.match_config import Team, PlayerConfig


def make_default_playlist() -> Playlist:

    # Choose which spawns you want to test.
    exercises = [
        #KickoffExercise('Both Corners', blue_spawns=[Spawns.CORNER_R, Spawns.CORNER_L], orange_spawns = []),
        #KickoffExercise('Right Corner 50/50', blue_spawns=[Spawns.CORNER_R], orange_spawns = [Spawns.CORNER_R]),
        KickoffExercise('Right Corner', blue_spawns=[Spawns.CORNER_R]),#, orange_spawns = [Spawns.CORNER_R]),
        KickoffExercise('Left Corner', blue_spawns=[Spawns.CORNER_L]),#, orange_spawns = [Spawns.CORNER_L]),
        KickoffExercise('Back Right', blue_spawns=[Spawns.BACK_R]),#, orange_spawns = [Spawns.BACK_R]),
        KickoffExercise('Back Left', blue_spawns=[Spawns.BACK_L]),#, orange_spawns = [Spawns.BACK_L]),
        KickoffExercise('Straight', blue_spawns=[Spawns.STRAIGHT]),#, orange_spawns = [Spawns.STRAIGHT]),
    ]

    for ex in exercises:
        ex.match_config.player_configs = [
            PlayerConfig.bot_config(
                Path(__file__).absolute().parent.parent / 'botimus.cfg', Team.BLUE
            ),
            # PlayerConfig.bot_config(
            #     Path(__file__).absolute().parent.parent.parent.parent / "Open source bots" / 'Kamael' / 'Kamael.cfg', Team.ORANGE
            # )
        ]

    return exercises