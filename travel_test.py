from rlutilities.simulation import Car
from maneuvers.driving.travel import TravelPlan, TravelMethod


def run_plan(plan: TravelPlan):
    print_plan_state(plan)
    dodges = 0
    while not plan.is_finished():
        method = plan.advance()
        if method == TravelMethod.Dodge:
            dodges += 1
        if dodges > 1:
            assert True
        print("--------:", method)
        print_plan_state(plan)

def print_plan_state(plan: TravelPlan):
    print("distance=" + str(plan.distance_traveled))
    print("forward_speed=" + str(plan.forward_speed))
    print("time_passed=" + str(plan.time_passed))
    print("boost=" + str(plan.boost))

car = Car()
car.boost = 0
best_t = 0
best_dist = 0
for threshold in range(1100, 1400, 1):
    print()
    print("T:", threshold)
    plan = TravelPlan(car, max_time=4.0)
    plan.DODGE_SPEED_THRESHOLD = threshold
    plan.DODGE_DURATION = 1.2
    run_plan(plan)
    if plan.distance_traveled > best_dist:
        best_dist = plan.distance_traveled
        best_t = threshold

print("best t:", best_t)