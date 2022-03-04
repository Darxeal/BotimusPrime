import time
from ctypes import create_unicode_buffer, windll

import keyboard
from rlbot.agents.base_script import BaseScript
from rlbot.utils.game_state_util import GameInfoState, GameState, BallState, Physics, Vector3


def is_rocket_league_focused() -> bool:
    # https://stackoverflow.com/questions/10266281/obtain-active-window-using-python
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    title = buf.value or ""
    return title.startswith("Rocket League")


def ignore_when_rl_not_focused_wrapper(func):
    def wrapper():
        if is_rocket_league_focused():
            func()

    return wrapper


# Extending the BaseScript class is purely optional. It's just convenient / abstracts you away from
# some strange classes like GameInterface
class MyScript(BaseScript):
    def __init__(self):
        super().__init__("Z-Drive")

    def run(self):
        def skip_slowmo():
            self.set_game_state(GameState(game_info=GameInfoState(game_speed=1)))

        def skip_goal():
            self.set_game_state(GameState(ball=BallState(Physics(Vector3(0, -5500, 500)))))

        actions = {
            "enter": skip_slowmo,
            "p": skip_goal,
        }
        for key, action in actions.items():
            keyboard.add_hotkey(key, ignore_when_rl_not_focused_wrapper(action))

        while True:
            self.renderer.begin_rendering("controls")
            controls_overlay_text = "\n".join(f"[{key}] {action.__name__}" for key, action in actions.items())
            self.renderer.draw_string_2d(1500, 50, 2, 2, controls_overlay_text, self.renderer.yellow())
            self.renderer.end_rendering()
            time.sleep(1.0)


# You can use this __name__ == '__main__' thing to ensure that the script doesn't start accidentally if you
# merely reference its module from somewhere
if __name__ == "__main__":
    script = MyScript()
    script.run()
