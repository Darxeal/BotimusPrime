from training.botimus_training import CollectorExcercise, Car, Ball
from rlutilities.linear_algebra import vec2, vec3, rotation, dot, look_at

class PowerslideCollection(CollectorExcercise):

    timeout = 1.2

    def set_car_ball_state(self, car: Car, ball: Ball):
        car.position[2] = 18
        car.velocity = vec3(1500, 0, 0)

        ball.position = vec3(2000,2000,2000)
