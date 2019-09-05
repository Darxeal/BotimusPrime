from dataclasses import dataclass

from tools.drawing import DrawingTool

from typing import List

@dataclass
class ManeuverHistoryEntry:
    target_y: float
    name: str 
    reason: str
    status: str
    y: float = 0
    scale: float = 0


class ManeuverHistory:

    main_text_x = 10
    main_text_y = 300

    def __init__(self):
        self.history: List[ManeuverHistoryEntry] = []

    def add(self, name: str, reason: str = "", status = ""):
        if len(self.history) > 0 and self.history[-1].name == name and self.history[-1].reason == reason:
            return
        for item in self.history:
            item.target_y -= 50
        self.history.append(ManeuverHistoryEntry(
            target_y=self.main_text_y,
            name=name,
            y=self.main_text_y + 100,
            reason=reason,
            status=status
        ))

    def render(self, draw: DrawingTool, num_of_items=4):
        first = True
        items_drawn = 0

        draw.group("history")


        for item in reversed(self.history):

            target_scale = 4 if first else 2
            item.scale += (target_scale - item.scale) / 3
            item.y += (item.target_y - item.y) / 10

            draw.color(draw.pink)
            draw.string2D(self.main_text_x, item.y, item.name, 2)
            draw.color(draw.cyan)
            draw.string2D(self.main_text_x + 200, item.y, item.reason, 2)
            draw.color(draw.white)
            draw.string2D(self.main_text_x + 400, item.y, item.status, 1)
            first = False
            items_drawn += 1

            if items_drawn > num_of_items:
                break 

        draw.group()