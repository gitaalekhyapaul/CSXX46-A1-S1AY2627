"""Assignment 1 - Problem 2 hierarchical-planning submission template.

* Group Member 1:
    - Name: Song Yuqiao
    - Matric number: A0332068H

* Group Member 2:
    - Name: Zhu Hao
    - Matric number: A0211201L

* Group Member 3:
    - Name: Lim Zi Qiang
    - Matric number: A0297855E

* Group Member 4:
    - Name: Paul Gita Alekhya
    - Matric number: A0328476R

* Collaborators: None
* Sources: None
"""

from __future__ import annotations

from itertools import islice
from numbers import Integral
from typing import Any, Sequence

from unified_planning.model.htn import HierarchicalProblem, Method
from unified_planning.shortcuts import (
    BoolType,
    Equals,
    Fluent,
    InstantaneousAction,
    Not,
    Object,
    OneshotPlanner,
    UserType,
)


# The representation below is fixed. Hidden tests change values, not the schema.
# Each request is a dictionary with exactly these five keys.
REQUEST_KEYS = {"start", "goal", "deadline", "base_utility", "late_penalty"}


def validate_config(config: dict[str, Any]) -> None:
    """Validate the public Problem 2 configuration schema."""
    required = {"num_levels", "elevator_start", "capacity", "requests"}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError(f"config must contain exactly these keys: {sorted(required)}")

    num_levels = config["num_levels"]
    elevator_start = config["elevator_start"]
    capacity = config["capacity"]
    requests = config["requests"]
    if (
        not isinstance(num_levels, int)
        or isinstance(num_levels, bool)
        or num_levels < 1
    ):
        raise ValueError("num_levels must be a positive integer")
    if (
        not isinstance(elevator_start, int)
        or isinstance(elevator_start, bool)
        or not 0 <= elevator_start < num_levels
    ):
        raise ValueError("elevator_start must name an existing floor")
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
        raise ValueError("capacity must be a positive integer")
    if not isinstance(requests, (list, tuple)):
        raise ValueError("requests must be a list or tuple")

    for request in requests:
        if not isinstance(request, dict) or set(request) != REQUEST_KEYS:
            raise ValueError(
                "each request must contain exactly: start, goal, deadline, "
                "base_utility, late_penalty"
            )
        for key in REQUEST_KEYS:
            value = request[key]
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"request {key} must be an integer")
        if not 0 <= request["start"] < num_levels:
            raise ValueError("request start must name an existing floor")
        if not 0 <= request["goal"] < num_levels:
            raise ValueError("request goal must name an existing floor")
        if request["deadline"] < 0:
            raise ValueError("deadline must be non-negative")
        if request["base_utility"] <= 0:
            raise ValueError("base_utility must be positive")
        if request["late_penalty"] <= 0:
            raise ValueError("late_penalty must be positive")


def validate_order(config: dict[str, Any], order: Sequence[int]) -> list[int]:
    """Return a normalized passenger permutation, safely rejecting bad iterables."""
    passenger_count = len(config["requests"])
    try:
        values = list(islice(iter(order), passenger_count + 1))
    except TypeError as error:
        raise ValueError("order must be an iterable of passenger indices") from error
    if (
        len(values) != passenger_count
        or any(
            not isinstance(index, Integral) or isinstance(index, bool)
            for index in values
        )
        or sorted(int(index) for index in values) != list(range(passenger_count))
    ):
        raise ValueError("order must contain every passenger index exactly once")
    return [int(index) for index in values]


def service_batches(config: dict[str, Any], order: Sequence[int]) -> list[list[int]]:
    """Split active passengers into consecutive capacity-sized batches."""
    order = validate_order(config, order)
    active = [
        index
        for index in order
        if config["requests"][index]["start"] != config["requests"][index]["goal"]
    ]
    capacity = config["capacity"]
    return [
        active[start : start + capacity] for start in range(0, len(active), capacity)
    ]


def evaluate_service_order(
    config: dict[str, Any], order: Sequence[int]
) -> dict[str, Any]:
    """Replay deterministic capacity batches using the external time model.

    Moving from floor ``a`` to floor ``b`` takes ``abs(a - b)`` time units.
    For each batch, all passengers board in order before anyone exits; they then
    exit in the same order. Opening, closing, loading, and unloading each take
    one time unit. Completion is measured immediately after unloading.
    """
    validate_config(config)
    order = validate_order(config, order)
    batches = service_batches(config, order)
    passenger_count = len(config["requests"])

    current_floor = config["elevator_start"]
    current_time = 0
    total_travel = 0
    completion_times = [0] * passenger_count

    for batch in batches:
        for index in batch:
            start = config["requests"][index]["start"]
            distance = abs(current_floor - start)
            total_travel += distance
            current_time += distance + 3  # move; open, load, close
            current_floor = start

        for index in batch:
            goal = config["requests"][index]["goal"]
            distance = abs(current_floor - goal)
            total_travel += distance
            current_time += distance + 2  # move; open, unload
            completion_times[index] = current_time
            current_time += 1  # close before the next task
            current_floor = goal

    utilities = []
    for request, completion_time in zip(config["requests"], completion_times):
        lateness = max(0, completion_time - request["deadline"])
        utilities.append(
            max(0, request["base_utility"] - request["late_penalty"] * lateness)
        )

    return {
        "order": order,
        "batches": batches,
        "completion_times": completion_times,
        "utilities": utilities,
        "total_utility": sum(utilities),
        "sum_completion_time": sum(completion_times),
        "max_completion_time": max(completion_times, default=0),
        "total_travel": total_travel,
        "finish_time": current_time,
    }


# COPY-FLAG-1-START


def choose_service_order(config):
    """Search batch orders, returning the best complete order found in time."""
    from itertools import permutations
    from time import perf_counter

    # This is real execution time, separate from simulated elevator time.
    # Use 8 seconds of the 10-second policy limit, leaving some headroom.
    stop_at = perf_counter() + 8.0
    validate_config(config)
    requests = config["requests"]
    capacity = config["capacity"]
    initial_floor = config["elevator_start"]

    # Index i always refers to the original config["requests"][i].
    # Parallel lists make repeated lookups simple during the search.
    starts = [r["start"] for r in requests]
    goals = [r["goal"] for r in requests]
    deadlines = [r["deadline"] for r in requests]
    values = [r["base_utility"] for r in requests]
    penalties = [r["late_penalty"] for r in requests]

    # Initially reached passengers need no elevator actions. Their utility is
    # fixed, so omit it from all search scores and bounds. Return their indices
    # at the end to satisfy the requirement that the result is a full permutation.
    active = tuple(i for i in range(len(requests)) if starts[i] != goals[i])
    completed = [i for i in range(len(requests)) if starts[i] == goals[i]]
    if not active:
        return completed

    def utility(i, completion):
        # Full value through the deadline, then a penalty, with a floor of zero.
        return max(0, values[i] - penalties[i] * max(0, completion - deadlines[i]))

    def run_batch(batch, floor, time):
        # Simulate one ordered batch. Every pickup precedes every delivery.
        # The elevator starts and ends each batch empty, with its door closed.
        gain = 0
        for i in batch:
            # Travel to the start, then open + load + close (three time units).
            time += abs(floor - starts[i]) + 3
            floor = starts[i]
        for i in batch:
            # Travel to the goal, then open + unload. Completion is recorded
            # now, before the following close-door action adds one more unit.
            time += abs(floor - goals[i]) + 2
            gain += utility(i, time)
            time += 1
            floor = goals[i]
        return floor, time, gain

    def score(order):
        # Evaluate a complete active-passenger order from the initial state.
        # Slicing creates capacity-sized batches, with a smaller final batch.
        floor, time, total = initial_floor, 0, 0
        for offset in range(0, len(order), capacity):
            batch = order[offset : offset + capacity]
            floor, time, gain = run_batch(batch, floor, time)
            total += gain
        return total

    # This complete order remains available if the search runs out of time.
    # best_value is earned utility for active passengers only.
    best_order = active
    best_value = score(active)

    class SearchTimeout(Exception):
        pass

    def check_time():
        # An exception exits all nested recursive calls at once. The outer
        # handler still returns the best complete order recorded so far.
        if perf_counter() >= stop_at:
            raise SearchTimeout

    def upper_bound(remaining, floor, time, earned):
        # Be deliberately optimistic about each remaining passenger:
        # direct travel via their start and goal, k pickups, then open + unload.
        # Actual routes must take at least this long. The estimates need not be
        # achievable together, so summing their utilities gives an upper bound.
        k = min(capacity, len(remaining))
        bound = earned
        for i in remaining:
            earliest = time + abs(floor - starts[i]) + abs(starts[i] - goals[i])
            earliest += 3 * k + 2
            bound += utility(i, earliest)
        return bound

    # For each (remaining passengers, floor), retain useful (time, utility) pairs.
    # An earlier state with at least equal earned utility dominates a later one.
    # Time/utility tradeoffs remain: earlier with less utility can still be useful.
    labels = {}

    def search(remaining, floor, time, earned, prefix):
        # remaining: active passenger indices still to serve.
        # floor, time: elevator position and elapsed time at a batch boundary.
        # earned: utility from passengers already served.
        # prefix: their service order, built one whole batch at a time.
        nonlocal best_order, best_value
        check_time()
        if not remaining:
            # A complete candidate can replace the saved answer.
            if earned > best_value:
                best_order, best_value = prefix, earned
            return
        # If even the optimistic future cannot win, stop this branch.
        if upper_bound(remaining, floor, time, earned) <= best_value:
            return

        key = (remaining, floor)
        previous = labels.setdefault(key, [])
        # A previously reached state can serve the same remaining passengers
        # from this floor, starting no later and with at least as much utility.
        if any(old_t <= time and old_v >= earned for old_t, old_v in previous):
            return
        # Discard older labels that this new state dominates, then retain it.
        previous[:] = [
            (old_t, old_v)
            for old_t, old_v in previous
            if not (time <= old_t and earned >= old_v)
        ]
        previous.append((time, earned))

        candidates = []
        k = min(capacity, len(remaining))
        # For remaining (A, B, C) and capacity 2, try ordered batches
        # (A,B), (A,C), (B,A), (B,C), (C,A), (C,B).
        for batch in permutations(remaining, k):
            check_time()
            next_floor, next_time, gain = run_batch(batch, floor, time)
            rest = tuple(i for i in remaining if i not in batch)
            bound = upper_bound(rest, next_floor, next_time, earned + gain)
            if bound > best_value:
                candidates.append((bound, gain, next_time, batch, rest, next_floor))

        # Explore higher bounds first, then higher batch gains, then earlier
        # finishes. This is an exploration preference, not a greedy commitment.
        candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
        for bound, gain, next_time, batch, rest, next_floor in candidates:
            # An earlier recursive call can have raised best_value.
            if bound > best_value:
                search(rest, next_floor, next_time, earned + gain, prefix + batch)

    try:
        # Different priorities supply several cheap starting candidates.
        # They are heuristics, so none is assumed to produce the best order.
        seeds = [
            # Earlier deadlines first.
            tuple(sorted(active, key=lambda i: deadlines[i])),
            # Faster utility loss first.
            tuple(sorted(active, key=lambda i: -penalties[i])),
            # Earlier time of reaching zero utility first.
            tuple(
                sorted(active, key=lambda i: deadlines[i] + values[i] / penalties[i])
            ),
            # Shorter direct trips from the initial elevator position first.
            tuple(
                sorted(
                    active,
                    key=lambda i: abs(initial_floor - starts[i])
                    + abs(starts[i] - goals[i]),
                )
            ),
        ]
        for order in seeds:
            check_time()
            value = score(order)
            if value > best_value:
                best_order, best_value = order, value

        # Improve the initial candidate with up to three passes of pair swaps.
        # Re-score the full order after each swap, including all later batches.
        # Only improving swaps are accepted. This can stop at a local best.
        for _ in range(3):
            improved = False
            for a in range(len(active)):
                for b in range(a + 1, len(active)):
                    check_time()
                    candidate = list(best_order)
                    candidate[a], candidate[b] = candidate[b], candidate[a]
                    value = score(candidate)
                    if value > best_value:
                        best_order, best_value = tuple(candidate), value
                        improved = True
            if not improved:
                break

        # Full base utility for everyone is an absolute ceiling. If a candidate
        # already reaches that ceiling, no recursive search is needed.
        # Otherwise, search past the local choices made by the seed/swap phase.
        if best_value < sum(values[i] for i in active):
            search(active, initial_floor, 0, 0, ())
    except SearchTimeout:
        # Budget expiry preserves a valid answer but does not prove it is best.
        pass

    # Appending initially reached passengers does not alter the active batches.
    return list(best_order) + completed


# COPY-FLAG-1-END


def generate_hierarchical(config: dict[str, Any]) -> HierarchicalProblem:
    """Build the elevator HTN for ``config`` using ``choose_service_order``."""
    validate_config(config)
    order = choose_service_order(config)
    # Validate the policy before any UP objects are constructed.
    evaluate_service_order(config, order)

    problem = HierarchicalProblem("ElevatorHTNProblem")

    Loc = UserType("Loc")
    Floor = UserType("Floor", father=Loc)
    Elevator = UserType("Elevator", father=Loc)
    Person = UserType("Person")
    Count = UserType("Count")

    floors = [Object(f"floor{i}", Floor) for i in range(config["num_levels"])]
    people = [Object(f"person{i + 1}", Person) for i in range(len(config["requests"]))]
    elevator = Object("elevator", Elevator)
    counts = [Object(f"c{i}", Count) for i in range(config["capacity"] + 1)]
    problem.add_objects(floors + people + [elevator] + counts)

    at_person = Fluent("at_person", Loc, person=Person)
    at_elevator = Fluent("at_elevator", Floor, elevator=Elevator)
    elevator_door_open = Fluent("elevator_door_open", BoolType(), elevator=Elevator)
    destination = Fluent("destination", Floor, person=Person)
    reached = Fluent("reached", BoolType(), person=Person)
    lift_count = Fluent("lift_count", BoolType(), count=Count)
    next_count = Fluent("next_count", BoolType(), current=Count, next=Count)
    problem.add_fluent(at_person)
    problem.add_fluent(at_elevator)
    problem.add_fluent(elevator_door_open)
    problem.add_fluent(destination)
    problem.add_fluent(reached, default_initial_value=False)
    problem.add_fluent(lift_count, default_initial_value=False)
    problem.add_fluent(next_count, default_initial_value=False)

    for person, request in zip(people, config["requests"]):
        problem.set_initial_value(at_person(person), floors[request["start"]])
        problem.set_initial_value(destination(person), floors[request["goal"]])
        if request["start"] == request["goal"]:
            problem.set_initial_value(reached(person), True)
    problem.set_initial_value(at_elevator(elevator), floors[config["elevator_start"]])
    problem.set_initial_value(elevator_door_open(elevator), False)
    problem.set_initial_value(lift_count(counts[0]), True)
    for index in range(config["capacity"]):
        problem.set_initial_value(next_count(counts[index], counts[index + 1]), True)

    move_elevator = InstantaneousAction(
        "move_elevator", elevator=Elevator, start=Floor, end=Floor
    )
    load = InstantaneousAction(
        "load",
        elevator=Elevator,
        person=Person,
        floor=Floor,
        current=Count,
        next=Count,
    )
    unload = InstantaneousAction(
        "unload",
        elevator=Elevator,
        person=Person,
        floor=Floor,
        previous=Count,
        current=Count,
    )
    open_door = InstantaneousAction("open_door", elevator=Elevator)
    close_door = InstantaneousAction("close_door", elevator=Elevator)

    # COPY-FLAG-2-START

    # Add the exact preconditions and effects listed in Task 2. Do not add
    # extra guards such as start != end or not reached on unload.

    move_elevator.add_precondition(Equals(at_elevator(move_elevator.elevator), move_elevator.start))
    move_elevator.add_precondition(Not(elevator_door_open(move_elevator.elevator)))
    move_elevator.add_effect(at_elevator(move_elevator.elevator), move_elevator.end)
    # Here a new effect replaces the old one, so no need to delete effect

    load.add_precondition(Equals(at_elevator(load.elevator), load.floor))
    load.add_precondition(Equals(at_person(load.person), load.floor))
    load.add_precondition(elevator_door_open(load.elevator))
    load.add_precondition(lift_count(load.current))
    load.add_precondition(next_count(load.current, load.next))
    load.add_precondition(Not(reached(load.person)))
    load.add_effect(at_person(load.person), load.elevator)
    load.add_effect(lift_count(load.current), False)
    load.add_effect(lift_count(load.next), True)

    unload.add_precondition(Equals(at_elevator(unload.elevator), unload.floor))
    unload.add_precondition(Equals(at_person(unload.person), unload.elevator))
    unload.add_precondition(elevator_door_open(unload.elevator))
    unload.add_precondition(Equals(destination(unload.person), unload.floor))
    unload.add_precondition(lift_count(unload.current))
    unload.add_precondition(next_count(unload.previous, unload.current))
    unload.add_effect(at_person(unload.person), unload.floor)
    unload.add_effect(reached(unload.person), True)
    unload.add_effect(lift_count(unload.current), False)
    unload.add_effect(lift_count(unload.previous), True)

    open_door.add_precondition(Not(elevator_door_open(open_door.elevator)))
    open_door.add_effect(elevator_door_open(open_door.elevator), True)
    
    close_door.add_precondition(elevator_door_open(close_door.elevator))
    close_door.add_effect(elevator_door_open(close_door.elevator), False)
    
    # COPY-FLAG-2-END

    problem.add_actions(
        [move_elevator, load, unload, open_door, close_door]
    )

    pickup_person = problem.add_task(
        "pickup_person", person=Person, start_floor=Floor
    )
    deliver_person = problem.add_task(
        "deliver_person", person=Person, goal_floor=Floor
    )
    confirm_reached = problem.add_task(
        "confirm_reached", person=Person, goal_floor=Floor
    )

    # COPY-FLAG-3-START

    # Add the five methods using the exact signatures, preconditions, and
    # ordered decompositions listed in Task 3.

    # Pickup from another floor: move, open, load, close.
    method = Method(
        "method_pickup_from_other_floor",
        elevator=Elevator, person=Person, elevator_floor=Floor,
        start_floor=Floor, current=Count, next=Count,
    )
    method.set_task(pickup_person, method.person, method.start_floor)
    method.add_precondition(Equals(at_person(method.person), method.start_floor))
    method.add_precondition(Equals(at_elevator(method.elevator), method.elevator_floor))
    method.add_precondition(Not(Equals(method.elevator_floor, method.start_floor)))
    method.add_precondition(Not(elevator_door_open(method.elevator)))
    method.add_precondition(lift_count(method.current))
    method.add_precondition(next_count(method.current, method.next))
    method.add_precondition(Not(reached(method.person)))
    move = method.add_subtask(
        move_elevator, method.elevator, method.elevator_floor, method.start_floor
    )
    opening = method.add_subtask(open_door, method.elevator)
    loading = method.add_subtask(
        load, method.elevator, method.person, method.start_floor,
        method.current, method.next,
    )
    closing = method.add_subtask(close_door, method.elevator)
    method.set_ordered(move, opening, loading, closing)
    problem.add_method(method)

    # Pickup on the current floor needs no movement.
    method = Method(
        "method_pickup_from_current_floor",
        elevator=Elevator, person=Person, start_floor=Floor,
        current=Count, next=Count,
    )
    method.set_task(pickup_person, method.person, method.start_floor)
    method.add_precondition(Equals(at_person(method.person), method.start_floor))
    method.add_precondition(Equals(at_elevator(method.elevator), method.start_floor))
    method.add_precondition(Not(elevator_door_open(method.elevator)))
    method.add_precondition(lift_count(method.current))
    method.add_precondition(next_count(method.current, method.next))
    method.add_precondition(Not(reached(method.person)))
    opening = method.add_subtask(open_door, method.elevator)
    loading = method.add_subtask(
        load, method.elevator, method.person, method.start_floor,
        method.current, method.next,
    )
    closing = method.add_subtask(close_door, method.elevator)
    method.set_ordered(opening, loading, closing)
    problem.add_method(method)

    # Delivery to another floor: move, open, unload, close.
    method = Method(
        "method_deliver_to_other_floor",
        elevator=Elevator, person=Person, elevator_floor=Floor,
        goal_floor=Floor, previous=Count, current=Count,
    )
    method.set_task(deliver_person, method.person, method.goal_floor)
    method.add_precondition(Equals(at_person(method.person), method.elevator))
    method.add_precondition(Equals(destination(method.person), method.goal_floor))
    method.add_precondition(Equals(at_elevator(method.elevator), method.elevator_floor))
    method.add_precondition(Not(Equals(method.elevator_floor, method.goal_floor)))
    method.add_precondition(Not(elevator_door_open(method.elevator)))
    method.add_precondition(lift_count(method.current))
    method.add_precondition(next_count(method.previous, method.current))
    move = method.add_subtask(
        move_elevator, method.elevator, method.elevator_floor, method.goal_floor
    )
    opening = method.add_subtask(open_door, method.elevator)
    unloading = method.add_subtask(
        unload, method.elevator, method.person, method.goal_floor,
        method.previous, method.current,
    )
    closing = method.add_subtask(close_door, method.elevator)
    method.set_ordered(move, opening, unloading, closing)
    problem.add_method(method)

    # Delivery on the current floor needs no movement.
    method = Method(
        "method_deliver_at_current_floor",
        elevator=Elevator, person=Person, goal_floor=Floor,
        previous=Count, current=Count,
    )
    method.set_task(deliver_person, method.person, method.goal_floor)
    method.add_precondition(Equals(at_person(method.person), method.elevator))
    method.add_precondition(Equals(destination(method.person), method.goal_floor))
    method.add_precondition(Equals(at_elevator(method.elevator), method.goal_floor))
    method.add_precondition(Not(elevator_door_open(method.elevator)))
    method.add_precondition(lift_count(method.current))
    method.add_precondition(next_count(method.previous, method.current))
    opening = method.add_subtask(open_door, method.elevator)
    unloading = method.add_subtask(
        unload, method.elevator, method.person, method.goal_floor,
        method.previous, method.current,
    )
    closing = method.add_subtask(close_door, method.elevator)
    method.set_ordered(opening, unloading, closing)
    problem.add_method(method)

    # Already completed requests only need verification, with no actions.
    method = Method("method_confirm_reached", person=Person, goal_floor=Floor)
    method.set_task(confirm_reached, method.person, method.goal_floor)
    method.add_precondition(reached(method.person))
    method.add_precondition(Equals(at_person(method.person), method.goal_floor))
    method.add_precondition(Equals(destination(method.person), method.goal_floor))
    problem.add_method(method)

    # COPY-FLAG-3-END

    # COPY-FLAG-4-START

    # Filter initially reached passengers, split the remaining order into
    # capacity-sized batches, add all pickups followed by all deliveries for
    # each batch, append confirm_reached tasks, and totally order the network.

    requests = config["requests"]
    active = [i for i in order if requests[i]["start"] != requests[i]["goal"]]
    completed = [i for i in order if requests[i]["start"] == requests[i]["goal"]]
    subtasks = []

    # Filter before batching so completed requests never occupy a batch slot.
    for offset in range(0, len(active), config["capacity"]):
        batch = active[offset : offset + config["capacity"]]
        for i in batch:
            subtasks.append(problem.task_network.add_subtask(
                pickup_person, people[i], floors[requests[i]["start"]]
            ))
        for i in batch:
            subtasks.append(problem.task_network.add_subtask(
                deliver_person, people[i], floors[requests[i]["goal"]]
            ))

    # Keep initially completed passengers in their relative policy order.
    for i in completed:
        subtasks.append(problem.task_network.add_subtask(
            confirm_reached, people[i], floors[requests[i]["goal"]]
        ))

    problem.task_network.set_ordered(*subtasks)

    # COPY-FLAG-4-END

    return problem


def solve(problem: HierarchicalProblem, verbose: bool = False):
    """Solve and return the planner result (printing it for notebook use)."""
    with OneshotPlanner(problem_kind=problem.kind) as planner:
        result = planner.solve(problem, timeout=10)
    if result.plan is not None:
        print("Plan:", repr(result.plan) if verbose else str(result.plan))
    else:
        print(result.status)
    return result


def main() -> None:
    config = {
        "num_levels": 5,
        "elevator_start": 2,
        "capacity": 2,
        "requests": [
            {
                "start": 0,
                "goal": 4,
                "deadline": 16,
                "base_utility": 100,
                "late_penalty": 8,
            },
            {
                "start": 3,
                "goal": 1,
                "deadline": 12,
                "base_utility": 80,
                "late_penalty": 12,
            },
            {
                "start": 2,
                "goal": 2,
                "deadline": 0,
                "base_utility": 30,
                "late_penalty": 5,
            },
        ],
    }
    order = choose_service_order(config)
    print("Service order:", order)
    print("External evaluation:", evaluate_service_order(config, order))
    solve(generate_hierarchical(config))


if __name__ == "__main__":
    main()
