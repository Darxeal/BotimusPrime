import queue
import time
from ctypes import create_unicode_buffer, windll

import keyboard
from rlbot.agents.base_script import BaseScript
from rlbot.utils.game_state_util import GameInfoState, GameState


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

        self.memory = []
        self.memory_index = -1
        self.gameplay_paused = False

    def pause(self):
        self.set_game_state(GameState(game_info=GameInfoState(paused=True)))

    def unpause(self):
        self.set_game_state(GameState(game_info=GameInfoState(paused=False)))

    def render_timeline(self):
        self.renderer.begin_rendering("timeline")
        timeline_string = "-" * self.memory_index + "o" + (len(self.memory) - self.memory_index - 1) * "-"
        self.renderer.draw_string_2d(10, 10, 1, 1, timeline_string, self.renderer.cyan())
        self.renderer.end_rendering()

    def checkpoint(self, packet, message):
        snapshot = GameState.create_from_gametickpacket(packet)
        snapshot.game_info = GameInfoState(paused=False)
        self.memory.append(snapshot)
        self.memory_index += 1
        self.render_timeline()

        self.gameplay_paused = True

        self.pause()

        def prev_snapshot():
            if self.memory_index > 0:
                self.memory_index -= 1
                self.render_timeline()
            self.set_game_state(self.memory[self.memory_index])
            self.wait_game_tick_packet()
            self.wait_game_tick_packet()
            self.pause()

        def next_snapshot():
            if self.memory_index < len(self.memory) - 1:
                self.memory_index += 1
                self.render_timeline()
            self.set_game_state(self.memory[self.memory_index])
            self.wait_game_tick_packet()
            self.wait_game_tick_packet()
            self.pause()

        def play():
            self.memory = self.memory[0:self.memory_index + 1]  # future is going to be rewritten
            self.unpause()
            self.gameplay_paused = False

        actions = {
            ",": prev_snapshot,
            "enter": play,
            ".": next_snapshot,
        }

        def play_action_factory(name):
            def play_action():
                self.matchcomms.outgoing_broadcast.put_nowait({
                    "event": "action_selected",
                    "action": name
                })
                time.sleep(0.1)
                play()

            play_action.__name__ = name
            return play_action

        if "actions" in message:
            for i, name in enumerate(message["actions"]):
                actions.update({str(i + 1): play_action_factory(name)})

        self.renderer.begin_rendering("controls")
        controls_overlay_text = "\n".join(f"[{key}] {action.__name__}" for key, action in actions.items())
        self.renderer.draw_string_2d(1500, 50, 2, 2, controls_overlay_text, self.renderer.yellow())
        self.renderer.end_rendering()

        for key, action in actions.items():
            keyboard.add_hotkey(key, ignore_when_rl_not_focused_wrapper(action))

        while self.gameplay_paused:
            time.sleep(0.1)

        keyboard.clear_all_hotkeys()
        self.renderer.clear_screen("controls")

    def run(self):
        print(self.matchcomms_root)
        while True:
            packet = self.wait_game_tick_packet()

            message = None
            while True:
                try:
                    message = self.matchcomms.incoming_broadcast.get_nowait()
                except queue.Empty:
                    break

            if message:
                print(message)
                if isinstance(message, dict) and message.get("event", "") == "checkpoint":
                    self.checkpoint(packet, message)


# You can use this __name__ == '__main__' thing to ensure that the script doesn't start accidentally if you
# merely reference its module from somewhere
if __name__ == "__main__":
    script = MyScript()
    script.run()
