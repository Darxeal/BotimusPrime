from training.botimus_training import BotimusStrikerExcercise, Car, Ball, SpecificManeuverStrikerExcercise
from rlutilities.linear_algebra import look_at, vec3
from utils.vector_math import ground_direction


class EasyShot(SpecificManeuverStrikerExcercise):

    maneuver_name = "DodgeShot"
    timeout = 7

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