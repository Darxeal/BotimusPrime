from maneuvers.kit import *
from maneuvers.strikes.strike import Strike


class WallStrike(Strike):

    max_dist_from_wall = 150

    def __init__(self, car, ball):
        super().__init__(car, ball)
        self.collision: ray = None

    def get_hit_direction(self):
        return None

    def get_distance_to_target(self):
        dist = self.arrive.get_total_distance()
        if self.car.position[2] < 200:
            dist += distance(self.arrive.target, self.collision.start)
        return dist

    def configure(self, intercept):
        s = sphere(intercept.position, self.max_dist_from_wall)
        self.collision = Field.collide(s)
        super().configure(intercept)

    def get_plane_intersect_position(self):
        target = self.collision.start
        my_pos = self.car.position
        distance_from_wall = abs(target[0] - my_pos[0])
        y = interpolate(0, -distance_from_wall, target[2] * 3, my_pos[1], target[1])
        return vec3(target[0], y, 0)

    def get_facing_target(self):
        return self.get_plane_intersect_position()

    def is_intercept_desirable(self):
        if self.intercept.position[2] < 200 or abs(self.intercept.position[0]) < 3000:
            return False

        return norm(self.collision.start) > 0

    def get_no_dodge_time(self):
        return math.inf

    def get_steer_penalty(self):
        return 0

    def get_offset_target(self):
        if self.car.position[2] > 100:
            return self.collision.start
        else:
            return self.get_plane_intersect_position()

    def render(self, draw: DrawingTool):
        draw.color(draw.lime)
        draw.circle(self.collision.start + self.collision.direction * 10, 93, self.collision.direction)

        plane_intersect_pos = self.get_plane_intersect_position()
        draw.color(draw.white)
        draw.line(ground(self.car.position), plane_intersect_pos)
        draw.line(plane_intersect_pos, self.collision.start)

        self.render_ball_prediction(draw)
