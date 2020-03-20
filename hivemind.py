from typing import Dict, Optional, List

from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.hivemind.python_hivemind import PythonHivemind

from maneuvers.maneuver import Maneuver
from rlutilities.simulation import Input, Car
from utils.drawing import DrawingTool
from utils.game_info import GameInfo


class Drone:
    def __init__(self, car: Car, index: int):
        self.car = car
        self.index = index
        self.controls: Input = Input()
        self.maneuver: Optional[Maneuver] = None


class BotimusHivemind(PythonHivemind):
    def __init__(self, *args):
        super().__init__(*args)
        self.info: GameInfo = None
        self.team: int = None
        self.draw: DrawingTool = None
        self.drones: List[Drone] = []

    def initialize_hive(self, packet: GameTickPacket) -> None:
        index = next(iter(self.drone_indices))
        self.team = packet.game_cars[index].team

        self.info = GameInfo(self.team)
        self.info.set_mode("soccar")
        self.draw = DrawingTool(self.renderer)
        self.drones = [Drone(self.info.cars[i], i) for i in self.drone_indices]

        self.logger.info('Botimus hivemind initialized')

    @staticmethod
    def to_player_input(controls: Input) -> PlayerInput:
        player_input = PlayerInput()
        player_input.throttle = controls.throttle
        player_input.steer = controls.steer
        player_input.pitch = controls.pitch
        player_input.yaw = controls.yaw
        player_input.roll = controls.roll
        player_input.jump = controls.jump
        player_input.boost = controls.boost
        player_input.handbrake = controls.handbrake
        return player_input

    def get_outputs(self, packet: GameTickPacket) -> Dict[int, PlayerInput]:
        self.info.read_packet(packet, self.get_field_info())

        return {drone.index: self.to_player_input(drone.controls) for drone in self.drones}
