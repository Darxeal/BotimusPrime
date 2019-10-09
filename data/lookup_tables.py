import csv
from typing import List
from bisect import bisect_left
from dataclasses import dataclass

class LookupTable:

    def __init__(self, file_name: str):
        self.file_name = file_name

    def get_column(self, name: str) -> List[float]:
        """
        Get all data in a column
        :param name: Name of the column
        :return: List of float values in the column
        """
        file = open(self.file_name)
        reader = csv.DictReader(file)
        return [float(row[name]) for row in reader]

    def find_index(self, column: List[float], value: float) -> int:
        return bisect_left(column, value, hi=len(column) - 1)


@dataclass
class LookupSimulationResult:
    speed_reached: float
    time_passed: float = 0.0
    distance_traveled: float = 0.0


class KinematicsLookupTable(LookupTable):

    def __init__(self, file_name: str):
        super().__init__(file_name)
        self.distances = self.get_column('player0_loc_y')
        self.times = self.get_column('time')
        self.speeds = self.get_column('player0_vel_y')
        assert self.distances
        assert self.times
        assert self.speeds

        # shift times so that it starts at 0
        t0 = self.times[0]
        for i in range(len(self.times)):
            self.times[i] -= t0

    def simulate_until_limit(self,
                            initial_speed: float,
                            time_limit: float = None,
                            distance_limit: float = None,
                            speed_limit: float = None) -> LookupSimulationResult:

        # atleast one limit must be set
        assert time_limit or distance_limit or speed_limit

        # limits must be positive
        if time_limit:
            assert time_limit > 0
        if speed_limit:
            assert speed_limit > 0
        if distance_limit:
            assert distance_limit > 0

        assert not speed_limit or speed_limit > initial_speed

        starting_index = self.find_index(self.speeds, initial_speed)
        # TODO: Interpolate
        initial_time = self.times[starting_index]
        initial_distance = self.distances[starting_index]


        final_indexes = []

        if time_limit:
            index = self.find_index(self.times, initial_time + time_limit)
            final_indexes.append(index)

        if distance_limit:
            index = self.find_index(self.distances, initial_distance + distance_limit)
            final_indexes.append(index)

        if speed_limit:
            index = self.find_index(self.speeds, speed_limit)
            final_indexes.append(index)

        final_index = min(final_indexes) # use the soonest reached limit

        # TODO: Interpolate values
        return LookupSimulationResult(self.speeds[final_index],
                                      self.times[final_index] - initial_time,
                                      self.distances[final_index] - initial_distance)

        

BOOST_LUT = KinematicsLookupTable('data/boost.csv')
THROTTLE_LUT = KinematicsLookupTable('data/throttle.csv')