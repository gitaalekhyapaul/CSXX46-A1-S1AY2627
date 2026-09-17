"""Assignment 1 - Problem 3 bonus free-form planning template.

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

Problem 3 uses exactly the same passenger schema, batching protocol, timing
model, and utility objective as Problem 2. Only the implementation method is
free: no HTN representation is required. The Python standard library, NumPy,
SciPy, OR-Tools, and PuLP are available in the grading environment. LLM tools
may assist development, but the submitted policy should not call a live LLM
API during grading.
"""

from __future__ import annotations

from itertools import islice
from numbers import Integral
from typing import Any, Sequence


REQUEST_KEYS = {"start", "goal", "deadline", "base_utility", "late_penalty"}


def validate_config(config: dict[str, Any]) -> None:
    """Validate the shared Problem 2/3 configuration schema."""
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
    """Return a normalized permutation of every passenger index."""
    count = len(config["requests"])
    try:
        values = list(islice(iter(order), count + 1))
    except TypeError as error:
        raise ValueError("order must be an iterable of passenger indices") from error
    if (
        len(values) != count
        or any(not isinstance(x, Integral) or isinstance(x, bool) for x in values)
        or sorted(int(x) for x in values) != list(range(count))
    ):
        raise ValueError("order must contain every passenger index exactly once")
    return [int(x) for x in values]


def service_batches(config: dict[str, Any], order: Sequence[int]) -> list[list[int]]:
    """Filter initially reached passengers and form deterministic batches."""
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
    """Evaluate an order using the grader-owned Problem 2 timing rules."""
    validate_config(config)
    order = validate_order(config, order)
    batches = service_batches(config, order)
    floor = config["elevator_start"]
    elapsed = 0
    travel = 0
    completion = [0] * len(config["requests"])
    for batch in batches:
        for index in batch:
            target = config["requests"][index]["start"]
            distance = abs(floor - target)
            travel += distance
            elapsed += distance + 3
            floor = target
        for index in batch:
            target = config["requests"][index]["goal"]
            distance = abs(floor - target)
            travel += distance
            elapsed += distance + 2
            completion[index] = elapsed
            elapsed += 1
            floor = target
    utilities = [
        max(
            0,
            request["base_utility"]
            - request["late_penalty"] * max(0, time - request["deadline"]),
        )
        for request, time in zip(config["requests"], completion)
    ]
    return {
        "order": order,
        "batches": batches,
        "completion_times": completion,
        "utilities": utilities,
        "total_utility": sum(utilities),
        "sum_completion_time": sum(completion),
        "total_travel": travel,
        "finish_time": elapsed,
    }


# COPY-FLAG-1-START

def choose_service_order(config: dict[str, Any]) -> list[int]:
    """Return the best order found by a budgeted exact/heuristic hybrid.

    A completed branch-and-bound search certifies optimality. Otherwise the
    remaining budget improves a valid incumbent without an optimality guarantee.
    """
    from itertools import permutations
    from random import Random
    from time import perf_counter

    # Reserve time within the grader's 2-second process limit for startup/return.
    stop = perf_counter() + 1.4
    validate_config(config)
    requests = config['requests']
    active = [i for i, r in enumerate(requests) if r['start'] != r['goal']]
    completed = [i for i, r in enumerate(requests) if r['start'] == r['goal']]
    n = len(active)
    if n <= 1:
        return active + completed
    rs = [requests[i] for i in active]
    starts = [r['start'] for r in rs]
    goals = [r['goal'] for r in rs]
    deadlines = [r['deadline'] for r in rs]
    values = [r['base_utility'] for r in rs]
    penalties = [r['late_penalty'] for r in rs]
    cap = min(config['capacity'], n)
    initial = config['elevator_start']
    ceiling = sum(values)
    rng = Random(5446)
    batches = {}
    scores = {}

    def batch_info(batch):
        data = batches.get(batch)
        if data is None:
            floor = starts[batch[0]]
            elapsed = 0
            stops = []
            for i in batch:
                elapsed += abs(floor - starts[i]) + 3
                floor = starts[i]
            for i in batch:
                elapsed += abs(floor - goals[i]) + 2
                stops.append((elapsed, deadlines[i], values[i], penalties[i]))
                elapsed += 1
                floor = goals[i]
            data = (starts[batch[0]], floor, elapsed, stops)
            batches[batch] = data
        return data

    def score(order):
        order = tuple(order)
        cached = scores.get(order)
        if cached is not None:
            return cached
        t, floor, utility, total_completion = 0, initial, 0, 0
        for offset in range(0, n, cap):
            batch = order[offset:offset + cap]
            start, end, duration, stops = batch_info(batch)
            t += abs(floor - start)
            for dt, deadline, value, penalty in stops:
                finish = t + dt
                total_completion += finish
                late = finish - deadline
                if late <= 0:
                    utility += value
                elif value > late * penalty:
                    utility += value - late * penalty
            t += duration
            floor = end
        # Utility is the only primary objective. Completion time breaks ties
        # to guide the search across equal-utility plateaus.
        result = (utility, -total_completion)
        # Keep memory bounded during long runs on easier configurations.
        if len(scores) < 100000:
            scores[order] = result
        return result

    seeds = [tuple(range(n))]
    for key in (
        lambda i: deadlines[i],
        lambda i: -penalties[i],
        lambda i: deadlines[i] + values[i] / penalties[i],
        lambda i: abs(initial - starts[i]) + abs(starts[i] - goals[i]),
        lambda i: goals[i],
        lambda i: starts[i],
    ):
        seeds.append(tuple(sorted(range(n), key=key)))
    best = max(seeds, key=score)
    best_score = score(best)
    if best_score[0] == ceiling:
        return [active[i] for i in best] + completed

    class BudgetExpired(Exception):
        pass

    evaluations = 0

    def consider(candidate, value):
        nonlocal best, best_score, evaluations
        evaluations += 1
        if value > best_score:
            best, best_score = tuple(candidate), value
        if best_score[0] == ceiling or (evaluations % 64 == 0 and perf_counter() >= stop):
            raise BudgetExpired

    def descend(order):
        order = tuple(order)
        current_score = score(order)
        while True:
            winner, winner_score = order, current_score
            for a in range(n):
                for b in range(a + 1, n):
                    candidate = list(order)
                    candidate[a], candidate[b] = candidate[b], candidate[a]
                    value = score(candidate)
                    consider(candidate, value)
                    if value > winner_score:
                        winner, winner_score = tuple(candidate), value
                for b in range(n):
                    if b == a:
                        continue
                    candidate = list(order)
                    candidate.insert(b, candidate.pop(a))
                    value = score(candidate)
                    consider(candidate, value)
                    if value > winner_score:
                        winner, winner_score = tuple(candidate), value
            if cap > 1:
                # Move short blocks across batch boundaries, preserving their order.
                for length in range(2, cap + 1):
                    for a in range(n - length + 1):
                        block = order[a:a + length]
                        rest = order[:a] + order[a + length:]
                        for b in range(len(rest) + 1):
                            if b == a:
                                continue
                            candidate = rest[:b] + block + rest[b:]
                            value = score(candidate)
                            consider(candidate, value)
                            if value > winner_score:
                                winner, winner_score = candidate, value
                # Swap complete full batches without disturbing their interiors.
                for a in range(0, n - cap + 1, cap):
                    for b in range(a + cap, n - cap + 1, cap):
                        candidate = list(order)
                        candidate[a:a + cap], candidate[b:b + cap] = candidate[b:b + cap], candidate[a:a + cap]
                        value = score(candidate)
                        consider(candidate, value)
                        if value > winner_score:
                            winner, winner_score = tuple(candidate), value
            if winner_score <= current_score:
                return order
            order, current_score = winner, winner_score

    class WarmupExpired(Exception):
        pass

    def upper_bound(remaining, floor, time, earned):
        overhead = 3 * min(cap, len(remaining)) + 2
        for i in remaining:
            earliest = time + abs(floor - starts[i]) + abs(starts[i] - goals[i]) + overhead
            earned += max(0, values[i] - penalties[i] * max(0, earliest - deadlines[i]))
        return earned

    labels = {}

    def search(remaining, floor, time, earned, prefix):
        if perf_counter() >= warmup_stop:
            raise WarmupExpired
        if not remaining:
            consider(prefix, score(prefix))
            return
        if upper_bound(remaining, floor, time, earned) <= best_score[0]:
            return
        previous = labels.setdefault((remaining, floor), [])
        if any(old_t <= time and old_v >= earned for old_t, old_v in previous):
            return
        previous[:] = [(t, v) for t, v in previous if not (time <= t and earned >= v)]
        previous.append((time, earned))
        candidates = []
        for batch in permutations(remaining, min(cap, len(remaining))):
            if perf_counter() >= warmup_stop:
                raise WarmupExpired
            start, end, duration, stops = batch_info(batch)
            arrival = time + abs(floor - start)
            gain = sum(max(0, v - p * max(0, arrival + dt - d)) for dt, d, v, p in stops)
            rest = tuple(i for i in remaining if i not in batch)
            bound = upper_bound(rest, end, arrival + duration, earned + gain)
            if bound > best_score[0]:
                candidates.append((bound, gain, arrival + duration, batch, rest, end))
        candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
        for bound, gain, next_time, batch, rest, end in candidates:
            if bound > best_score[0]:
                search(rest, end, next_time, earned + gain, prefix + batch)

    elite = []
    try:
        elite.append(descend(best))
        # A small exact-search budget solves easy cases and offers a different
        # exploration path before the heuristic search consumes the remainder.
        warmup_stop = min(stop, perf_counter() + 0.25)
        try:
            search(tuple(range(n)), initial, 0, 0, ())
        except WarmupExpired:
            pass
        else:
            return [active[i] for i in best] + completed
        for seed in sorted(set(seeds), key=score, reverse=True):
            local = descend(seed)
            if local not in elite:
                elite.append(local)
        iteration = 0
        while perf_counter() < stop:
            iteration += 1
            elite = sorted(set(elite + [best]), key=score, reverse=True)[:8]
            candidate = list(best if iteration % 3 else rng.choice(elite))
            if iteration % 11 == 0:
                rng.shuffle(candidate)
            else:
                for _ in range(2 + iteration % 4):
                    a, b = rng.sample(range(n), 2)
                    if rng.randrange(2):
                        candidate[a], candidate[b] = candidate[b], candidate[a]
                    else:
                        candidate.insert(b, candidate.pop(a))
            elite.append(descend(candidate))
    except BudgetExpired:
        pass
    return [active[i] for i in best] + completed


# COPY-FLAG-1-END


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
        ],
    }
    order = choose_service_order(config)
    print("Service order:", order)
    print("Evaluation:", evaluate_service_order(config, order))


if __name__ == "__main__":
    main()
