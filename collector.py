from rlbot.agents.base_agent import BaseAgent, GameTickPacket, SimpleControllerState
from rlutilities.simulation import Input
from rlutilities.linear_algebra import rotation_to_euler, vec3
from utils.game_info import GameInfo
from pathlib import Path
from csv import DictWriter
from maneuvers.driving.drive import Drive


class Collector(BaseAgent):
    
    filename = "data/powerslide_1000.csv"

    def initialize_agent(self):
        self.info = GameInfo(self.index, self.team)
        self.controls: Input = Input()
        self.ticks = 0
        self.fieldnames = [
            "time",
            "ball_loc_x",
            "ball_loc_y",
            "ball_loc_z",
            "ball_vel_x",
            "ball_vel_y",
            "ball_vel_z",
            "ball_ang_x",
            "ball_ang_y",
            "ball_ang_z",
            "car_throttle",
            "car_steer",
            "car_pitch",
            "car_yaw",
            "car_roll",
            "car_jump",
            "car_boost",
            "car_handbrake",
            "car_loc_x",
            "car_loc_y",
            "car_loc_z",
            "car_rot_pitch",
            "car_rot_yaw",
            "car_rot_roll",
            "car_vel_x",
            "car_vel_y",
            "car_vel_z",
            "car_ang_x",
            "car_ang_y",
            "car_ang_z"
        ]
        self.memory = []
        self.drive = Drive(self.info.my_car)
        self.starting_time = 0

    def get_output(self, game_tick_packet: GameTickPacket):
        self.info.read_packet(game_tick_packet, self.get_field_info())
        self.ticks += 1

        if self.ticks > 5:
            if len(self.memory) == 0:
                self.starting_time = self.info.time

            game = self.info
            ball = game.ball
            car = game.my_car
            pyr = rotation_to_euler(car.orientation)
            self.memory.append({
                "time": str(game.time - self.starting_time),
                "ball_loc_x": str(ball.position[0]),
                "ball_loc_y": str(ball.position[1]),
                "ball_loc_z": str(ball.position[2]),
                "ball_vel_x": str(ball.velocity[0]),
                "ball_vel_y": str(ball.velocity[1]),
                "ball_vel_z": str(ball.velocity[2]),
                "ball_ang_x": str(ball.angular_velocity[0]),
                "ball_ang_y": str(ball.angular_velocity[1]),
                "ball_ang_z": str(ball.angular_velocity[2]),
                "car_throttle": str(self.controls.throttle),
                "car_steer": str(self.controls.steer),
                "car_pitch": str(self.controls.pitch),
                "car_yaw": str(self.controls.yaw),
                "car_roll": str(self.controls.roll),
                "car_jump": str(int(self.controls.jump)),
                "car_boost": str(int(self.controls.boost)),
                "car_handbrake": str(int(self.controls.handbrake)),
                "car_loc_x": str(car.position[0]),
                "car_loc_y": str(car.position[1]),
                "car_loc_z": str(car.position[2]),
                "car_vel_x": str(car.velocity[0]),
                "car_vel_y": str(car.velocity[1]),
                "car_vel_z": str(car.velocity[2]),
                "car_ang_x": str(car.angular_velocity[0]),
                "car_ang_y": str(car.angular_velocity[1]),
                "car_ang_z": str(car.angular_velocity[2]),
                "car_rot_pitch": str(pyr[0]),
                "car_rot_yaw": str(pyr[1]),
                "car_rot_roll": str(pyr[2]),
            })

        self.drive.target_pos = vec3(0,0,0)
        self.drive.step(self.info.time_delta)
        self.controls = self.drive.controls

        return self.controls

    def retire(self):
        print("Writing to file...")
        with open(str(Path(__file__).absolute().parent / self.filename), 'w', newline='') as file:
            writer = DictWriter(file, fieldnames=self.fieldnames)
            writer.writeheader()
            for slice in self.memory:
                writer.writerow(slice)
            self.memory = []
        print("done")
