"""
Tool for running unit test for groups of bots (e.g. hivemind)

The file structure is important:
- Each folder codes for a match configuration file.
- Each python module inside codes for one test.
- This file is one folder above the test folders.
"""

import os
import time
import keyboard
import importlib.util

from queue import Queue
from threading import Thread

from rlbot.setup_manager import SetupManager
from rlbot.utils.game_state_util import GameState
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.python_version_check import check_python_version
from rlbot.utils.structures.game_interface import GameInterface


class Message:
    READY = 0
    DONE = 1


# folder name: [filenames]
TESTS = {
    "single_bot": ["ceiling_recovery1", "ceiling_recovery2"],
    # "three_bots": ["random"],
}


RESET_KEY = "r"
NEXT_KEY = "p"


# TODO
# Send some description of the test to render.
# Evaluate unit tests and give score.


def run_state_setting(my_queue: Queue):
    """Controls state setting for tests."""
    message = my_queue.get()
    if message != Message.READY:
        raise Exception(f"Got {message} instead of READY")

    logger = get_logger("UTSS")  # Unit Test State Setting
    game_interface = GameInterface(logger)
    game_interface.load_interface()
    game_interface.wait_until_loaded()
    logger.info("Running!")

    # Get the first GameState.
    game_state, message = my_queue.get()
    game_interface.set_game_state(game_state)

    while True:
        while my_queue.qsize() == 0:
            # Sleep to prevent reset-spamming.
            time.sleep(0.1)

            if not keyboard.is_pressed(RESET_KEY):
                continue

            # Reset the GameState.
            logger.info("Resetting test.")
            game_interface.set_game_state(game_state)

        # Receive GameState.
        logger.info("Setting new test.")
        game_state, message = my_queue.get()
        if message == Message.DONE:
            print('Thread 2 closing.')
            exit()

        game_interface.set_game_state(game_state)


# Really hacky :(
def get_game_state(module_path):
    """Imports the GAME_STATE from a module"""
    spec = importlib.util.spec_from_file_location("test", location=f"{module_path}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if isinstance(module.GAME_STATE, GameState):
        return module.GAME_STATE
    else:
        raise Exception(f"GAME_STATE is not an instance of GameState in {module_path}")


def run_tests(my_queue: Queue):
    """Runs the tests."""
    check_python_version()
    manager = SetupManager()

    has_started = False

    for config in TESTS:
        if len(TESTS[config]) == 0:
            continue

        # Start a match.
        directory = os.path.abspath(os.path.dirname(__file__))
        config_location = os.path.join(directory, config, "match.cfg")
        manager.load_config(config_location=config_location)
        manager.connect_to_game()
        manager.launch_early_start_bot_processes()
        manager.start_match()
        manager.launch_bot_processes()

        if not has_started:
            # Let other thread know that game has been launched.
            my_queue.put(Message.READY)
            has_started = True

        # Load first test for this config.
        test_num = 0
        my_queue.put(
            (
                get_game_state(os.path.join(directory, config, TESTS[config][test_num])),
                None
            )
        )

        while not manager.quit_event.is_set():
            manager.try_recieve_agent_metadata()

            # Move onto the next test.
            if keyboard.is_pressed(NEXT_KEY):
                test_num += 1

                # If we have exceeded the number of tests in this config,
                # break and go to the next config.
                if len(TESTS[config]) <= test_num:
                    break

                # Loads the next test.
                my_queue.put(
                    (
                        get_game_state(os.path.join(directory, config, TESTS[config][test_num])),
                        None
                    )
                )

                # Prevent accidental multiple key presses.
                time.sleep(1)

        # Kill all bot processes.
        manager.shut_down(kill_all_pids=True)

    my_queue.put((None, Message.DONE))
    print("Thread 1 closing.")
    exit()


if __name__ == "__main__":

    q = Queue()
    test_runner_thread = Thread(target=run_tests, args=(q, ))
    test_runner_thread.start()
    state_setting_thread = Thread(target=run_state_setting, args=(q, ))
    state_setting_thread.start()
    
    q.join()
    test_runner_thread.join()
    state_setting_thread.join()
