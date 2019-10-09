from data.lookup_tables import BOOST_LUT, THROTTLE_LUT, KinematicsLookupTable
import math
from enum import Enum
from rlutilities.simulation import Car
from rlutilities.linear_algebra import dot

class TravelMethod(Enum):
    Throttle = 1
    Boost = 2
    Dodge = 3
    Wavedash = 4


class TravelPlan:

    MAX_THROTTLE_SPEED = 1410
    MAX_SPEED = 2300
    BOOST_DEPLETION = 100.0 / 3.0
    DODGE_FORWARD_IMPULSE = 500
    DODGE_DURATION = 1.4
    DODGE_SPEED_THRESHOLD = 1200
    DODGE_SPEED_THRESHOLD_WITH_BOOST = 1800

    def __init__(self, car: Car, max_distance: float = math.inf, max_time: float = math.inf):
        self.forward_speed = dot(car.forward(), car.velocity)
        self.boost = car.boost
        self.time_passed = 0
        self.distance_traveled = 0

        self.max_distance = max_distance
        self.max_time = max_time

    def get_time_to_finish(self, additional_speed: float = 0.0):
        time_limit = self.max_time - self.time_passed
        distance_left = self.max_distance - self.distance_traveled
        speed = max(self.forward_speed + additional_speed, 1)
        distance_time_limit = distance_left / speed

        return min(time_limit, distance_time_limit)

    def is_finished(self):
        return self.get_time_to_finish() < 0.01

    def accelerate_until_speed(self, target_speed: float, with_boost: bool):
        lut = BOOST_LUT if with_boost else THROTTLE_LUT
        time_limit = self.max_time - self.time_passed

        # make sure we don't simulate longer than we can boost
        if with_boost:
            time_we_can_boost = self.boost / self.BOOST_DEPLETION
            time_limit = min(time_we_can_boost, time_limit)

        result = lut.simulate_until_limit(self.forward_speed,
                time_limit=time_limit,
                distance_limit=self.max_distance - self.distance_traveled,
                speed_limit=target_speed)

        self.forward_speed = result.speed_reached
        self.time_passed += result.time_passed
        self.distance_traveled += result.distance_traveled

        if with_boost:
            self.boost -= result.time_passed * self.BOOST_DEPLETION
            self.boost = max(self.boost, 0)

    def dodge(self):
        self.forward_speed += self.DODGE_FORWARD_IMPULSE
        self.forward_speed = min(self.MAX_SPEED, self.forward_speed)
        self.distance_traveled += self.forward_speed * self.DODGE_DURATION
        self.time_passed += self.DODGE_DURATION

    def maintain_speed_till_finish(self):
        time_left = self.get_time_to_finish()
        self.time_passed += time_left
        self.distance_traveled += time_left * self.forward_speed

    def advance(self) -> TravelMethod:
        # if we are close to max speed, boosting or dodging
        # no longer makes sense, so just throttle to keep speed
        if self.forward_speed > self.MAX_SPEED - 50:
            self.maintain_speed_till_finish()
            return TravelMethod.Throttle

        if self.boost > 0:

            # accelerate until we reach a speed where it's faster to dodge or
            # we run out of boost or we reach the target
            if self.forward_speed < self.DODGE_SPEED_THRESHOLD_WITH_BOOST:
                self.accelerate_until_speed(self.DODGE_SPEED_THRESHOLD_WITH_BOOST, with_boost=True)
                return TravelMethod.Boost

            # if we have enough time left for a dodge, do it
            time_left = self.get_time_to_finish(self.DODGE_FORWARD_IMPULSE)
            if time_left > self.DODGE_DURATION:
                self.dodge()
                return TravelMethod.Dodge
            
            # otherwise just boost until we reach max speed
            self.accelerate_until_speed(self.MAX_SPEED, with_boost=True)
            return TravelMethod.Boost

        # accelerate until we reach a speed where it's faster to dodge
        # or we reach the target
        if self.forward_speed < self.DODGE_SPEED_THRESHOLD:
            self.accelerate_until_speed(self.DODGE_SPEED_THRESHOLD, with_boost=False)
            return TravelMethod.Throttle


        # if we have enough time left for a dodge, do it
        time_left = self.get_time_to_finish(self.DODGE_FORWARD_IMPULSE)
        if time_left > self.DODGE_DURATION:
            self.dodge()
            return TravelMethod.Dodge
        
        if self.forward_speed < self.MAX_THROTTLE_SPEED:
            self.accelerate_until_speed(self.MAX_THROTTLE_SPEED, with_boost=False)
        else:
            # after MAX_THROTTLE_SPEED, we don't gain any acceleration from throttle,
            # and because we can't accelerate in any other way when we reach this line,
            # all we can do is just throttle to keep speed until we reach target
            self.maintain_speed_till_finish()

        return TravelMethod.Throttle

    def simulate(self):
        while not self.is_finished():
            self.advance()
