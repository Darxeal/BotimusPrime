from maneuvers.kit import *

from maneuvers.driving.arrive import Arrive

class FastRecovery(Maneuver):
    '''Boost down and try to land on all four wheels'''

    def __init__(self, car: Car):
        super().__init__(car)

        self.turn = AerialTurn(car, look_at(vec3(0, 0, -1)))
        self.landing = False

    def step(self, dt):
        self.turn.step(dt)
        self.controls = self.turn.controls
        self.controls.throttle = 1 # in case we're turtling

        if self.landing:
            self.turn.find_landing_orientation(200)
        else:
            # boost down
            if angle_between(self.car.forward(), vec3(0, 0, -1)) < 0.5:
                self.controls.boost = 1
            else:
                self.controls.boost = 0

            # when nearing landing position, start recovery
            if distance(self.car, self.find_landing_pos()) < clamp(norm(self.car.vel), 600, 2300):
                self.landing = True
                self.turn = AerialTurn(self.car)

        self.finished = self.car.on_ground

    def find_landing_pos(self, num_points=200, dt=0.0333) -> vec3:
        '''Simulate car falling until it hits a plane and return it's final position'''
        dummy = Car(self.car)
        for i in range(0, num_points):
            dummy.step(Input(), dt)
            dummy.time += dt
            n = dummy.pitch_surface_normal()
            if norm(n) > 0.0 and i > 10:
                return dummy.pos
        return self.car.pos
                    