from maneuvers.kit import *
from maneuvers.driving.arrive import Arrive


class Strike(Maneuver):

    max_additional_time = 0.5
    update_interval = 0.5

    def __init__(self, car: Car, ball: Ball, target: vec3):
        super().__init__(car)
        
        self.ball: Ball = ball
        self.target: vec3 = target

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
            self.configure(copy)

            if self.is_intercept_reachable():
                if self.is_intercept_desirable():
                    self.__previous_intercept_time = self.intercept.time
                    if previous_intercept_reachable:
                        self.arrive.speed_control = True
                    return
                previous_intercept_reachable = True

        print("Didn't find a valid intercept in time.")
        self.finished = True

    def get_hit_direction(self) -> vec3:
        target_direction = ground_direction(self.intercept, self.target)
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

    def get_no_dodge_time(self) -> float:
        return 1.0

    def is_intercept_reachable(self) -> bool:
        distance_to_target = self.get_distance_to_target()
        plan = TravelPlan(self.car, max_time=self.get_time_left())
        plan.no_dodge_time = self.get_no_dodge_time()
        plan.simulate()
        return plan.distance_traveled >= distance_to_target

    def is_intercept_desirable(self) -> bool:
        raise NotImplementedError

    def render(self, draw: DrawingTool):
        self.arrive.render(draw)

        draw.color(draw.lime)
        draw.circle(ground(self.intercept.position), 93)
        draw.point(self.intercept.position)

        if self.target is not None:
            draw.color(draw.cyan)
            pos = ground(self.intercept.position)
            tdir = ground_direction(pos, self.target)
            draw.triangle(pos + tdir * 150, tdir, length=100)

        if not self.__rendered_prediction:
            draw.group("prediction")
            self.__rendered_prediction = True
            draw.color(draw.yellow)
            draw.polyline(self.__ball_positions)
