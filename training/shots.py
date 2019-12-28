from training.botimus_training import BotimusStrikerExcercise, Car, Ball
from rlbottraining.training_exercise import Playlist
from rlutilities.linear_algebra import look_at, vec3
from rlbot.matchcomms.common_uses.set_attributes_message import make_set_attributes_message
from rlbot.matchcomms.common_uses.reply import send_and_wait_for_replies


class EasyShot(BotimusStrikerExcercise):

    timeout = 5

    def on_briefing(self):
        send_and_wait_for_replies(self.get_matchcomms(), [
            make_set_attributes_message(0, {'matchcomms_message' : 'DodgeShot'})
        ])

    def set_car_ball_state(self, car: Car, ball: Ball):
        ball.position[0] = self.rng.n11() * 1000
        ball.position[1] = 3000
        ball.position[2] = 200

        ball.velocity[0] = self.rng.n11() * 500
        ball.velocity[1] = self.rng.n11() * 500
        ball.velocity[2] = 0

        car.position[0] = self.rng.n11() * 1000
        car.position[1] = 0
        car.position[2] = 20
        car.orientation = look_at(ball.position, vec3(0,0,1))
        car.boost = 30

def make_default_playlist() -> Playlist:
    return [
        EasyShot(),
        EasyShot()
    ]