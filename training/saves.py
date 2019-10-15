from training.botimus_training import BotimusGoalieExcercise, Car, Ball, SpecificManeuverGoalieExcercise
from rlutilities.linear_algebra import look_at, vec3, axis_to_rotation


class EasySave(SpecificManeuverGoalieExcercise):
    timeout = 5
    maneuver_name = "Offense"

    def set_car_ball_state(self, car: Car, ball: Ball):
        car.position = vec3(0, -5000, 20)
        car.orientation = look_at(vec3(0,1,0), vec3(0,0,1))
        car.boost = 10

        ball.position = vec3(0, 0, 500)
        ball.velocity = vec3(0, -2000, 0)


class FullTurnSave(SpecificManeuverGoalieExcercise):
    timeout = 5
    maneuver_name = "Offense"

    def set_car_ball_state(self, car: Car, ball: Ball):
        car.position = vec3(300, -3000, 20)
        car.orientation = look_at(vec3(0,-1,0), vec3(0,0,1))
        car.velocity = vec3(0,-self.rng.uniform(1500.0, 2000.0),0)
        car.boost = 10

        ball.position = vec3(0, 2000, 300)
        ball.velocity = vec3(self.rng.n11() * 300, self.rng.uniform(-2000,-3000), 0)