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
    """Return every passenger index exactly once.

    Replace this valid baseline with any algorithm you choose. A hidden test is
    accepted if the returned order reaches at least 98% of the optimal total
    utility within the 2-second process limit.
    """
    validate_config(config)
    return list(range(len(config["requests"])))


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
