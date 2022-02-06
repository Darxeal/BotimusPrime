import time
from dataclasses import dataclass
from typing import List, Callable

from rlbot.utils.game_state_util import GameState, GameInfoState
from rlbot.utils.rendering.rendering_manager import RenderingManager

from tools.drawing import DrawingTool
from tools.math import lerp


@dataclass
class Announcement:
    message: str
    time_added: float


@dataclass
class Explanation:
    message: str
    time_last_active: float
    color: tuple = DrawingTool.yellow
    active = True


class Announcer:
    announcements: List[Announcement] = []
    explanations: List[Explanation] = []

    new_announcement_wants_slowmo = False
    is_currently_slowmo = False
    slowmo_end_time = 0.0

    slowmo_speed = 0.05
    slowmo_duration = 1.5

    @classmethod
    def announce(cls, message: str, slowmo=True):
        cls.announcements.append(Announcement(message, time.time()))

        if slowmo:
            cls.new_announcement_wants_slowmo = True

    @classmethod
    def explain(cls, message: str, slowmo=True, color=None):
        now = time.time()
        for e in cls.explanations:
            if e.message == message:
                e.time_last_active = now
                e.active = True
                break
        else:
            cls.explanations.append(Explanation(message, now, color) if color else Explanation(message, now))

        if slowmo:
            cls.new_announcement_wants_slowmo = True

    @classmethod
    def step(cls, set_state: Callable[[GameState], None], renderer: RenderingManager):
        now = time.time()

        # begin slowmo
        if cls.new_announcement_wants_slowmo:
            cls.new_announcement_wants_slowmo = False
            if not cls.is_currently_slowmo:
                set_state(GameState(game_info=GameInfoState(game_speed=0.3)))
                cls.is_currently_slowmo = True
            cls.slowmo_end_time = now + cls.slowmo_duration

        # end slowmo
        elif cls.is_currently_slowmo and now >= cls.slowmo_end_time:
            set_state(GameState(game_info=GameInfoState(game_speed=1.0)))
            cls.is_currently_slowmo = False

        cls.announcements.sort(key=lambda a: a.time_added)
        del cls.announcements[:-10]

        if renderer.is_rendering():
            renderer.end_rendering()
        renderer.begin_rendering("announcer")

        # render announcements
        box_x, box_y = 20, 500
        box_margin = 10
        line_height = 20

        renderer.draw_rect_2d(box_x - box_margin, box_y - box_margin, 500,
                              len(cls.announcements) * line_height + box_margin * 2, True,
                              renderer.create_color(150, 0, 0, 0))

        for i, announcement in enumerate(cls.announcements):
            dt = now - announcement.time_added
            if dt > 5.0:
                continue
            lerp_t = min(1.0, dt)
            color = renderer.create_color(255, int(lerp(255, 0, lerp_t)), 255, 255)  # white -> cyan
            renderer.draw_string_2d(box_x + lerp(200, 0, lerp_t ** 0.1), box_y + i * line_height, 1, 1,
                                    announcement.message, color)

        # render explanations
        box_y = 200
        renderer.draw_rect_2d(box_x - box_margin, box_y - box_margin, 500, 10 * line_height + box_margin * 2, True,
                              renderer.create_color(150, 0, 0, 0))

        fade_duration = 10.0
        i = 0
        for explanation in cls.explanations:
            dt = now - explanation.time_last_active
            if dt > fade_duration:
                continue
            lerp_t = dt / fade_duration
            color = renderer.create_color(255, *explanation.color) if explanation.active else \
                renderer.create_color(int(lerp(255, 0, lerp_t)), 0, 255, 255)
            renderer.draw_string_2d(box_x, box_y + i * line_height, 1, 1, explanation.message, color)
            explanation.active = False
            i += 1
