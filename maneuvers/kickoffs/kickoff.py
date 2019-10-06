from maneuvers.kit import *

from maneuvers.driving.arrive import Arrive

from rlutilities.mechanics import Dodge

class Kickoff(Maneuver):
    '''The simplest boost and dodge at the end kickoff.'''
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info = info

        self.action = Arrive(car)
        self.action.target = info.ball.position
        self.action.target_direction = direction(info.ball, info.their_goal.center)
        self.action.lerp_t = 0.4
        self.action.allow_dodges_and_wavedashes = False

        self.dodging = False
        self.dodge = Dodge(car)
        self.dodge.duration = 0.05
        self.dodge.direction = normalize(vec2(info.their_goal.center))

    def step(self, dt):
        if not self.dodging and distance(self.car, self.info.ball) < 800:

            # detect if an opponent is going for kickoff
            is_opponent_going_for_kickoff = False
            for opponent in self.info.opponents:
                if distance(self.info.ball, opponent) < 1500:
                    is_opponent_going_for_kickoff = True

            if is_opponent_going_for_kickoff:
                self.action = self.dodge
                self.dodging = True
            else:
                # if not, don't dodge and steer a bit to the side to aim for a top-corner
                self.action.target = self.info.ball.position + vec3(100, 0, 0)

        self.action.step(dt)
        self.controls = self.action.controls
        self.finished = self.info.ball.position[0] != 0

    def render(self, draw: DrawingTool):
        if not self.dodging:
            self.action.render(draw)
