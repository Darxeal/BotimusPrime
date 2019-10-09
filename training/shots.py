from training.botimus_training import BotimusStrikerExcercise, Car, Ball
from rlutilities.linear_algebra import look_at, vec3
from rlbot.matchcomms.common_uses.set_attributes_message import make_set_attributes_message
from rlbot.matchcomms.common_uses.reply import send_and_wait_for_replies
from utils.vector_math import ground_direction


class EasyShot(BotimusStrikerExcercise):

    timeout = 7

    def on_briefing(self):
        send_and_wait_for_replies(self.get_matchcomms(), [
            make_set_attributes_message(0, {'matchcomms_message' : 'DodgeShot'})
        ])

    def set_car_ball_state(self, car: Car, ball: Ball):
        ball.position[0] = self.rng.n11() * 500
        ball.position[1] = 1000
        ball.position[2] = 800

        ball.velocity[0] = self.rng.n11() * 1000
        ball.velocity[1] = self.rng.n11() * 500
        ball.velocity[2] = 0

        car.position[0] = self.rng.n11() * 500
        car.position[1] = -5000
        car.position[2] = 20
        tdir = ground_direction(car, ball)
        car.orientation = look_at(tdir, vec3(0,0,1))
        car.velocity = tdir * 0
        car.boost = 0