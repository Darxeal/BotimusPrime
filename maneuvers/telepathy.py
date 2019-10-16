from maneuvers.kit import *
from maneuvers.strikes.strike import Strike
from maneuvers.driving.arrive import Arrive


class Telepathy(Maneuver):

    def __init__(self, car: Car, info: GameInfo, opponent_strike: Strike):
        super().__init__(car)
        self.opponent_strike: Strike = opponent_strike
        self.info: GameInfo = info
        self.arrive = Arrive(car)
        self.arrive.target_direction = normalize(info.their_goal.center)
        self.arrive.arena_clamp = 200

    def step(self, dt):
        self.opponent_strike.step(dt)

        ball_speed = norm(self.opponent_strike.intercept.velocity) + self.opponent_strike.car_speed_at_intercept + 500
        ball_direction = ground_direction(self.opponent_strike.intercept, self.info.my_goal.center)
        ball_pos = ground(self.opponent_strike.intercept)
        ball_time = self.opponent_strike.intercept.time

        delta_time = 0.1
        self.arrive.target = ball_pos
        while Arena.inside(ball_pos):
            ball_time += delta_time
            ball_pos += ball_direction * ball_speed * delta_time

            self.arrive.target = ball_pos
            # facing_direction = ground_direction(self.car, ball_pos)
            # team_sign = 1 if self.car.team == 1 else -1
            # if sgn(facing_direction[1]) != team_sign:
            #     facing_direction = vec3(sgn(facing_direction[0]), 0, 0)
            # self.arrive.target_direction = facing_direction

            time_left = ball_time - self.car.time
            if self.arrive.estimate_time() < time_left:
                break

        self.arrive.step(dt)
        self.controls = self.arrive.controls

        if (
            (self.opponent_strike.finished
            or ground_distance(self.car.position, self.arrive.target) < 2000)
            and self.arrive.travel.driving
        ):
            self.finished = True

    def render(self, draw: DrawingTool):
        draw.color(draw.pink)
        draw.line(ground(self.opponent_strike.intercept), self.arrive.target)
        self.arrive.render(draw)
        self.opponent_strike.render(draw)



