"""
Small script for starting matches quickly from saved match configs.

Usage:
    python config_runner.py path/to/your/config.cfg
"""

import sys
import os
import traceback
from rlbot.setup_manager import SetupManager


def run_match(file_path):
    assert os.path.exists(file_path), f"Invalid path: {file_path}"
    _, ext = os.path.splitext(file_path)
    assert ext == ".cfg", f"Wrong file extension: '{ext}', expected '.cfg'"

    print(f"Using config at {file_path}")
    
    manager = SetupManager()
    manager.load_config(config_location=file_path)

    try:
        manager.connect_to_game()
        manager.launch_early_start_bot_processes()
        manager.start_match()
        manager.launch_bot_processes()
    except Exception:
        traceback.print_exc()
    finally:
        manager.shut_down(kill_all_pids=True)


if __name__ == "__main__":
    # Use like this:
    # python config_runner.py some_path\to_your\config.cfg
    args = sys.argv
    assert len(args) == 2, f"Wrong number of arguments ({len(args)})"
    file_path = os.path.abspath(args[1])
    run_match(file_path)
    