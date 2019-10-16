from maneuvers.kit import *

from maneuvers.strikes.strike import Strike
from maneuvers.jumps.aim_dodge import AimDodge


class GroundStrike(Strike):

    max_intercept_height = 120
    max_intercept_velocity = 100

    def is_intercept_desirable(self):
        return (
            self.intercept.position[2] < self.max_intercept_height
            and abs(self.intercept.velocity[2]) < self.max_intercept_velocity
            and distance(self.intercept.velocity, self.get_hit_direction() * self.car_speed_at_intercept) > 1000
        )

    def configure_mechanics(self):
        super().configure_mechanics()
        self.arrive.lerp_t = 0.53

    def get_offset_target(self):
        return ground(self.intercept) - self.get_hit_direction() * 90
