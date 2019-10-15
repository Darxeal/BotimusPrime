from maneuvers.kit import *
from maneuvers.driving.arrive import Arrive


class Strike(Maneuver):

    max_additional_time = 0.1
    update_interval = 0.3

    def __init__(self, car: Car, ball: Ball):
        Maneuver.__init__(self, car)
        
        self.ball: Ball = ball
        self.target_direction: vec3 = None
        self.earliest_intercept_time: float = 0.0

        self.arrive: Arrive = Arrive(car)
        self.intercept: Ball = None
        self.__ball_positions: List[vec3] = []
        self.__last_update_time: float = -math.inf
        self.__previous_intercept_time: float = self.car.time + 10.0
        self.__rendered_prediction = True

    def step(self, dt):
        if self.should_recalculate_intercept():
            self.recalculate_intercept()

        self.configure(self.intercept)
        self.arrive.step(dt)
        self.controls = self.arrive.controls
        if self.arrive.finished:
            self.finished = True
        
    def should_recalculate_intercept(self) -> bool:
        return self.car.time > self.__last_update_time + self.update_interval and self.car.on_ground
    
    def recalculate_intercept(self):
        copy = Ball(self.ball)
        dt = 1.0 / 120.0
        self.__rendered_prediction = False
        self.__ball_positions.clear()
        self.__last_update_time = self.car.time
        last_pos_time = 0.0
        previous_intercept_reachable = False

        while copy.time < self.__previous_intercept_time + self.max_additional_time:
            copy.step(dt)
            if copy.time > last_pos_time + 0.2:
                self.__ball_positions.append(vec3(copy.position))
                last_pos_time = copy.time
            
            if copy.time > self.car.time + 10.0:
                break

            self.configure(copy)
            if self.is_intercept_reachable():
                if self.is_intercept_desirable() and copy.time > self.earliest_intercept_time:
                    self.__previous_intercept_time = self.intercept.time
                    if previous_intercept_reachable:
                        self.arrive.speed_control = True
                    return
                previous_intercept_reachable = True

        print("Didn't find a valid intercept in time.")
        self.finished = True

    def get_target_direction(self) -> vec3:
        return self.target_direction

    def get_hit_direction(self) -> vec3:
        target_direction = self.get_target_direction()
        return ground_direction(self.intercept.velocity, target_direction * 5000)

    def configure(self, intercept: Ball):
        self.intercept = intercept
        self.configure_mechanics()

    def configure_mechanics(self):
        self.arrive.car = self.car
        self.arrive.target = self.get_offset_target()
        self.arrive.target_direction = self.get_hit_direction()
        self.arrive.time = self.intercept.time
        self.arrive.travel.no_dodge_time = self.get_no_dodge_time()

    def get_offset_target(self) -> vec3:
        raise NotImplementedError

    def get_facing_target(self) -> vec3:
        return self.arrive.get_shifted_target()

    def get_distance_to_target(self) -> float:
        return self.arrive.get_total_distance()

    def get_time_left(self) -> float:
        return self.intercept.time - self.car.time

    def get_steer_penalty(self) -> float:
        # return 0
        if norm(self.car.velocity) < 1000:
            return 0
        # stolen from reliefbot
        to_target = direction(self.car.position, self.get_facing_target())
        correction_err = max(0.0, 0.3 - dot(to_target, self.car.forward()))
        return correction_err * norm(self.car.velocity) * .02

    def get_no_dodge_time(self) -> float:
        return 1.0

    def is_intercept_reachable(self) -> bool:
        distance_to_target = self.get_distance_to_target()
        plan = TravelPlan(self.car, max_time=self.get_time_left() - self.get_steer_penalty())
        plan.no_dodge_time = self.get_no_dodge_time()
        plan.simulate()
        return plan.distance_traveled > distance_to_target - 30

    def is_intercept_desirable(self) -> bool:
        raise NotImplementedError

    def render_ball_prediction(self, draw: DrawingTool):
        if not self.__rendered_prediction:
            draw.group("prediction")
            self.__rendered_prediction = True
            draw.color(draw.yellow)
            draw.polyline(self.__ball_positions)

    def render_intercept_circle(self, draw: DrawingTool):
        draw.color(draw.lime)
        draw.circle(ground(self.intercept.position), 93)
        draw.point(self.intercept.position)

    def render_direction_triangle(self, draw: DrawingTool):
        draw.color(draw.cyan)
        tdir = self.get_target_direction()
        draw.triangle(ground(self.intercept.position) + tdir * 150, tdir, length=100)

    def render(self, draw: DrawingTool):
        self.arrive.render(draw)
        self.render_direction_triangle(draw)
        self.render_intercept_circle(draw)
        self.render_ball_prediction(draw)



