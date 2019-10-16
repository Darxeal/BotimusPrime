from maneuvers.kit import *
from maneuvers.driving.drive import Drive
from maneuvers.jumps.half_flip import HalfFlip
from rlutilities.mechanics import Wavedash, Dodge
from utils.travel_plan import TravelMethod, TravelPlan


class Travel(Maneuver):

    def __init__(self, car: Car):
        super().__init__(car)
        self.target: vec3 = vec3(0,0,0)
        self.no_dodge_time = 0

        self.driving = True
        self.dodging = False

        self.drive = Drive(car)
        self.dodge: Dodge = None

        self.__time_spend_on_ground = 0

    def get_plan(self):
        distance_to_target = ground_distance(self.car.position, self.target)
        plan = TravelPlan(self.car, max_distance=distance_to_target)
        plan.no_dodge_time = self.no_dodge_time
        return plan

    def time_for_distance(self, dist: float) -> float:
        plan = TravelPlan(self.car, max_distance=dist)
        plan.no_dodge_time = self.no_dodge_time
        plan.simulate()
        return plan.time_passed

    def estimate_time_to(self, target: vec3) -> float:
        distance_to_target = ground_distance(self.car.position, target)
        return self.time_for_distance(distance_to_target)

    def step(self, dt):
        if self.dodging:
            self.dodge.step(dt)
            self.controls = self.dodge.controls

            if self.car.on_ground:
                self.__time_spend_on_ground += dt
            else:
                self.__time_spend_on_ground = 0

            if self.dodge.finished and self.car.on_ground and self.__time_spend_on_ground > 0.2:
                self.dodging = False
                self.driving = True
        else:
            self.drive.target_pos = self.target
            self.drive.step(dt)
            self.controls = self.drive.controls

            plan = self.get_plan()
            method = plan.advance()

            if method == TravelMethod.Boost:
                self.controls.boost = True
                self.controls.throttle = 1

            elif method == TravelMethod.Throttle:
                self.controls.boost = False
                self.controls.throttle = 1

            elif (
                method == TravelMethod.Dodge
                and angle_to(self.car, self.target) < 0.1
                and self.car.position[2] < 100
            ):
                self.dodging = True
                self.driving = False
                self.dodge = Dodge(self.car)
                self.dodge.duration = 0.1
                self.dodge.direction = vec2(ground_direction(self.car.position, self.target))

            if angle_to(self.car, self.target) > 0.5:
                self.controls.boost = False


    def render(self, draw: DrawingTool):
        if self.dodging:
            draw.string(self.car.position, "dodging")
            return

        self.drive.render(draw)

        # draw.group("TravelPlan")
        plan = self.get_plan()
        last_pos = self.car.position
        target_dir = ground_direction(last_pos, self.target)
        while not plan.is_finished():
            method = plan.advance()
            new_pos = self.car.position + target_dir \
                * plan.distance_traveled

            if method == TravelMethod.Throttle:
                draw.color(draw.white)
                draw.line(last_pos, new_pos)

            if method == TravelMethod.Boost:
                draw.color(draw.lime)
                draw.line(last_pos, new_pos)

            if method == TravelMethod.Dodge:
                dummy = Car()
                dummy.orientation = look_at(target_dir, vec3(0,0,1))
                draw.color(draw.cyan)
                dummy.position = last_pos
                draw.car_shadow(dummy)
                dummy.position = new_pos
                draw.car_shadow(dummy)

            draw.string(new_pos, plan.forward_speed)
            last_pos = new_pos