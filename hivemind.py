import logging
from typing import Dict, List

from rlbot.agents.hivemind.python_hivemind import PythonHivemind
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.game_data_struct import GameTickPacket

from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.refuel import Refuel
from rlutilities.linear_algebra import vec3
from strategy.hivemind_strategy import HivemindStrategy
from utils.drawing import DrawingTool
from utils.drone import Drone
from utils.game_info import GameInfo


RELEASE = True

class Beehive(PythonHivemind):
    def __init__(self, *args):
        super().__init__(*args)
        self.info: GameInfo = None
        self.team: int = None
        self.draw: DrawingTool = None
        self.drones: List[Drone] = []
        self.strategy: HivemindStrategy = None

        self.last_latest_touch_time = 0.0

    def initialize_hive(self, packet: GameTickPacket) -> None:
        index = next(iter(self.drone_indices))
        self.team = packet.game_cars[index].team

        self.info = GameInfo(self.team)
        self.info.set_mode("soccar")
        self.strategy = HivemindStrategy(self.info, self.logger)
        self.draw = DrawingTool(self.renderer, self.team)
        self.drones = [Drone(self.info.cars[i], i) for i in self.drone_indices]

        self.logger.handlers[0].setLevel(logging.NOTSET)  # override handler level
        self.logger.setLevel(logging.INFO if RELEASE else logging.DEBUG)
        self.logger.info("Beehive initialized")

    def get_outputs(self, packet: GameTickPacket) -> Dict[int, PlayerInput]:
        self.info.read_packet(packet, self.get_field_info())

        # if a kickoff is happening and none of the drones have a Kickoff maneuver active, reset all drone maneuvers
        if (
            packet.game_info.is_kickoff_pause
            and self.info.ball.position[0] == 0 and self.info.ball.position[1] == 0
            and not any(isinstance(drone.maneuver, Kickoff) for drone in self.drones)
        ):
            self.strategy.set_kickoff_maneuvers(self.drones)

        # reset drone maneuvers when an opponent hits the ball
        touch = packet.game_ball.latest_touch
        if touch.time_seconds > self.last_latest_touch_time and touch.team != self.team:
            self.last_latest_touch_time = touch.time_seconds
            for drone in self.drones:
                if drone.maneuver and drone.maneuver.interruptible():  # don't reset a drone while dodging/recovering
                    drone.maneuver = None

        # reset drone maneuver when it gets demoed
        for drone in self.drones:
            if drone.maneuver and drone.car.demolished:
                drone.maneuver = None

        # if at least one drone doesn't have an active maneuver, execute strategy code
        if None in [drone.maneuver for drone in self.drones]:
            self.logger.debug("Setting maneuvers")
            self.strategy.set_maneuvers(self.drones)

        for drone in self.drones:
            if drone.maneuver is None:
                continue

            # execute maneuvers
            drone.maneuver.step(self.info.time_delta)
            drone.controls = drone.maneuver.controls

            drone.maneuver.render(self.draw)

            # draw names of maneuvers above our drones
            self.draw.color(self.draw.yellow)
            self.draw.string(drone.car.position + vec3(0, 0, 50), type(drone.maneuver).__name__)

            # expire finished maneuvers
            if drone.maneuver.finished:
                drone.maneuver = None

        # demo avoidance
        collisions = self.info.detect_collisions(time_limit=0.2, dt=1/60)
        for collision in collisions:
            index1, index2, time = collision
            self.logger.debug(f"Collision: {index1} ->*<- {index2} in {time:.2f} seconds.")
            if time <= 0.2:
                for drone in self.drones:
                    if (
                        (drone.index == index1 or drone.index == index2)
                        and isinstance(drone.maneuver, (ShadowDefense, Refuel))
                        ):
                        self.logger.debug(f"Drone {drone.index} is avoiding the collision!")
                        drone.controls.jump = True
                        break

        # render predictions
        # for prediction in [self.info.predict_car_drive(i) for i in range(self.info.num_cars)]:
        #     self.draw.color(self.draw.yellow)
        #     self.draw.polyline(prediction)

        self.strategy.render(self.draw)
        self.draw.execute()
        return {drone.index: drone.get_player_input() for drone in self.drones}
