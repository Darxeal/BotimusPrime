from training.botimus_training import SpecificManeuverTest, Car, Ball
from rlutilities.linear_algebra import vec2, vec3, rotation, dot, look_at

class TurnAndTravelTest(SpecificManeuverTest):

    timeout = 2
    maneuver_name = "TurnAndTravel"

    def randomly_rotated_vec2(self) -> vec2:
        return dot(rotation(self.rng.uniform(0.0, 3.14 * 2)), vec2(1, 0))

    def set_car_ball_state(self, car: Car, ball: Ball):
        car.position[2] = 18
        td = vec3(self.randomly_rotated_vec2())
        car.orientation = look_at(td, vec3(0,0,1))
        car.velocity = td * 2000

        ball.position = vec3(self.randomly_rotated_vec2()) * 3000

class SlideAndTravelTest(SpecificManeuverTest):

    timeout = 2
    maneuver_name = "SlideAndTravel"

    def randomly_rotated_vec2(self) -> vec2:
        return dot(rotation(self.rng.uniform(0.0, 3.14 * 2)), vec2(1, 0))

    def set_car_ball_state(self, car: Car, ball: Ball):
        car.position[2] = 18
        td = vec3(self.randomly_rotated_vec2())
        car.orientation = look_at(td, vec3(0,0,1))
        car.velocity = td * 1000

        ball.position = vec3(self.randomly_rotated_vec2()) * 3000
