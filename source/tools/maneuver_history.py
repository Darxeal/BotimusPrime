from dataclasses import dataclass

from tools.drawing import DrawingTool

@dataclass
class ManeuverHistoryEntry:
    target_y: float
    name: str 
    reason: str
    y: float = 0
    scale: float = 0


class ManeuverHistory:

    main_text_x = 200
    main_text_y = 500

    def __init__(self):
        self.history: list = []

    def add(self, name: str, reason: str = ""):
        if len(self.history) > 0 and self.history[-1].name == name and self.history[-1].reason == reason:
            return
        for item in self.history:
            item.target_y += 70
        self.history.append(ManeuverHistoryEntry(
            target_y=self.main_text_y,
            name=name,
            y=self.main_text_y - 100,
            reason=reason
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
            draw.string2D(self.main_text_x, item.y, item.name, item.scale)
            draw.color(draw.cyan)
            draw.string2D(self.main_text_x + 50, item.y + 30, item.reason, item.scale)
            first = False
            items_drawn += 1

            if items_drawn > num_of_items:
                break