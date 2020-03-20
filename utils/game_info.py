from typing import List

from rlutilities.simulation import Game, Car, Ball, Pad
from rlutilities.linear_algebra import vec3


class Goal:

    WIDTH = 1784.0
    HEIGHT = 640.0
    DISTANCE = 5120.0

    def __init__(self, team):
        sign = -1 if team == 0 else 1
        self.center = vec3(0, sign * Goal.DISTANCE, Goal.HEIGHT / 2.0)
        self.team = team

    def inside(self, pos) -> bool:
        return pos[1] < -Goal.DISTANCE if self.team == 0 else pos[1] > Goal.DISTANCE


class GameInfo(Game):

    def __init__(self, team):
        super().__init__(0, team)
        self.my_goal = Goal(team)
        self.their_goal = Goal(1 - team)

        self.ball_predictions: List[Ball] = []
        self.about_to_score = False
        self.about_to_be_scored_on = False
        self.time_of_goal = -1

        self.large_boost_pads: List[Pad] = []

    def read_packet(self, packet, field_info):
        self.read_game_information(packet, field_info)
        self.large_boost_pads = self.get_large_boost_pads()
        
    def get_large_boost_pads(self) -> List[Pad]:
        return [self.pads[3], 
                self.pads[4], 
                self.pads[15],
                self.pads[18],
                self.pads[29],
                self.pads[30]]

    def get_teammates(self, car: Car) -> List[Car]:
        return [self.cars[i] for i in range(self.num_cars)
                if self.cars[i].team == self.team and self.cars[i].id != car.id]

    def get_opponents(self, car: Car) -> List[Car]:
        return [self.cars[i] for i in range(self.num_cars) if self.cars[i].team != car.team]

    def predict_ball(self, time_limit=6.0, dt=1/120):
        self.about_to_score = False
        self.about_to_be_scored_on = False
        self.time_of_goal = -1

        self.ball_predictions = []
        prediction = Ball(self.ball)

        while prediction.time < self.ball.time + time_limit:
            prediction.step(dt)
            self.ball_predictions.append(Ball(prediction))

            if self.time_of_goal == -1:
                if self.my_goal.inside(prediction.position):
                    self.about_to_be_scored_on = True
                    self.time_of_goal = prediction.time
                if self.their_goal.inside(prediction.position):
                    self.about_to_score = True
                    self.time_of_goal = prediction.time
