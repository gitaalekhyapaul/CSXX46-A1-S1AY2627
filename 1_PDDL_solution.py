"""
Assignment 1 - Problem 1 PDDL submission template.

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
"""

### AFTER YOU COMPLETE 1_PDDL.ipynb, COPY THE MARKED SECTIONS HERE ###

# COPY-FLAG-1 and COPY-FLAG-2 are required for the complete notebook workflow
# to run, but they carry no marks. COPY-FLAG-3 and COPY-FLAG-4 are graded.


# OPTIONAL, UNGRADED AI-AUDIT NOTES
#
# You may record your answers to the notebook's AI-audit activities below.
# The autograder does not read this variable, and leaving it blank has no
# effect on your score. Do not include an AI transcript; concise technical
# conclusions are enough.
optional_ai_audit_notes = r"""
1. AI draft check
   Assumption or invariant examined:
   Smallest counterexample tested:
   Revision made, if any:

2. Fragment 1 (loading while the door may be closed)
   Violated invariant:
   Concrete counterexample:
   Smallest repair:

3. Fragment 2 (incorrect movement effect)
   Violated invariant:
   Concrete counterexample:
   Smallest repair:

4. Fragment 3 (using each passenger's start as the goal)
   Violated invariant:
   Concrete counterexample:
   Smallest repair:

5. Capacity extension
   Why the unload count-link direction decrements occupancy:
   What can happen if load omits (not (reached ?p)):
"""


# COPY-FLAG-1-START

pddl_domain = """
(define (domain elevator)
  (:requirements :strips :typing :negative-preconditions)
  (:types level person)

  (:predicates
    (elevator_at ?l - level) ; The elevator is at a specific level
    (person_at ?p - person ?l - level) ; A person is at a specific level
    (person_in_elevator ?p - person) ; A person is in the elevator
    (elevator_empty) ; The elevator is empty
    (door_open ?l - level) ; The door is open at a specific level
    (adjacent_up ?from ?to - level) ; Defines that ?to is the level above ?from
    (adjacent_down ?from ?to - level) ; Defines that ?to is the level below ?from
  )

  ; move_up: The elevator can only move up one level
  (:action move_up
    :parameters (?from ?to - level)
    :precondition (and
        (elevator_at ?from)
        (not (door_open ?from))
        (adjacent_up ?from ?to)
    ) ; FILL IN the precondition for move_up with one or more predicates
    :effect (and
        (not (elevator_at ?from))
        (elevator_at ?to)
    ) ; FILL IN the effect for move_up with one or more predicates
  )

  ; move_down: The elevator can only move down one level
  (:action move_down
    :parameters (?from ?to - level)
    :precondition (and
        (elevator_at ?from)
        (not (door_open ?from))
        (adjacent_down ?from ?to)
    ) ; FILL IN the precondition for move_down with one or more predicates
    :effect (and
        (not (elevator_at ?from))
        (elevator_at ?to)
    ) ; FILL IN the effect for move_down with one or more predicates
  )

  ; open_door: Open the door without considering picking up people
  (:action open_door
    :parameters (?l - level)
    :precondition (and
        (elevator_at ?l)
        (not (door_open ?l))
    ) ; FILL IN the precondition for open_door with one or more predicates
    :effect (and
        (door_open ?l)
    ) ; FILL IN the effect for open_door with one or more predicates
  )

  ; close_door: Close the door
  (:action close_door
    :parameters (?l - level)
    :precondition (and
        (elevator_at ?l)
        (door_open ?l)
    ) ; FILL IN the precondition for close_door with one or more predicates
    :effect (and
        (not (door_open ?l))
    ) ; FILL IN the effect for close_door with one or more predicates
  )

  ; load: Pick up a person, requires the door to be open and the elevator to be empty
  (:action load
    :parameters (?p - person ?l - level)
    :precondition (and
        (person_at ?p ?l)
        (elevator_at ?l)
        (door_open ?l)
        (elevator_empty)
    ) ; FILL IN the precondition for load with one or more predicates
    :effect (and
        (person_in_elevator ?p)
        (not (person_at ?p ?l))
        (not (elevator_empty))
    ) ; FILL IN the effect for load with one or more predicates
  )

  ; unload: Drop off a person, requires the door to be open and the person to be in the elevator
  (:action unload
    :parameters (?p - person ?l - level)
    :precondition (and
        (person_in_elevator ?p)
        (elevator_at ?l)
        (door_open ?l)
    ) ; FILL IN the precondition for unload with one or more predicates
    :effect (and
        (person_at ?p ?l)
        (not (person_in_elevator ?p))
        (elevator_empty)
    ) ; FILL IN the effect for unload with one or more predicates
  )
)
"""

# COPY-FLAG-1-END


def generate_pddl_domain(output_file="elevator_domain.pddl"):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(pddl_domain)


def validate_config(config):
    """Validate the fixed configuration schema used in Problem 1."""
    required = {"num_levels", "elevator_start", "requests"}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError(f"config must contain exactly these keys: {sorted(required)}")

    num_levels = config["num_levels"]
    elevator_start = config["elevator_start"]
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
    if not isinstance(requests, (list, tuple)):
        raise ValueError("requests must be a list or tuple of (start, goal) pairs")

    for request in requests:
        if not isinstance(request, (list, tuple)) or len(request) != 2:
            raise ValueError("each request must be a (start, goal) pair")
        start, goal = request
        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(goal, int)
            or isinstance(goal, bool)
        ):
            raise ValueError("request floors must be integers")
        if not 0 <= start < num_levels or not 0 <= goal < num_levels:
            raise ValueError("request floors must name existing floors")


# COPY-FLAG-2-START

def generate_pddl_from_config(config, output_file):
    validate_config(config)
    num_levels = config["num_levels"]
    elevator_start = config["elevator_start"]
    requests = config["requests"]
    persons = [f"person{i + 1}" for i in range(len(requests))]

    pddl = "(define (problem elevator_problem)\n"
    pddl += "  (:domain elevator)\n"
    levels = " ".join(f"level{i}" for i in range(num_levels))
    pddl += "  (:objects\n"
    pddl += f"    {levels} - level\n"
    if persons:
        pddl += f"    {' '.join(persons)} - person\n"
    pddl += "  )\n\n"

    pddl += "  (:init\n"
    pddl += f"    (elevator_at level{elevator_start})\n"  # Use elevator_start
    pddl += "    (elevator_empty)\n"
    for person, (start, _goal) in zip(persons, requests):
        pddl += f"    (person_at {person} level{start})\n"  # Place person at start
    for floor in range(num_levels - 1):
        pddl += f"    (adjacent_up level{floor} level{floor + 1})\n"  # Upward adjacency
        pddl += f"    (adjacent_down level{floor + 1} level{floor})\n"  # Downward adjacency
    pddl += "  )\n\n"

    pddl += "  (:goal\n    (and\n"
    for person, (_start, goal) in zip(persons, requests):
        pddl += f"      (person_at {person} level{goal})\n"  # Place person at their goal
    pddl += "    )\n  )\n)"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(pddl)
    return pddl

# COPY-FLAG-2-END


def validate_capacity_config(config):
    """Validate the fixed schema for the capacity extension."""
    required = {"num_levels", "elevator_start", "capacity", "requests"}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError(f"config must contain exactly these keys: {sorted(required)}")
    validate_config(
        {key: config[key] for key in ("num_levels", "elevator_start", "requests")}
    )
    capacity = config["capacity"]
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
        raise ValueError("capacity must be a positive integer")


# COPY-FLAG-3-START

pddl_domain_capacity = """
(define (domain elevator)
  (:requirements :strips :typing :negative-preconditions)
  (:types level person count)

  (:predicates
    (elevator_at ?l - level)
    (person_at ?p - person ?l - level)
    (person_in_elevator ?p - person)
    (destination ?p - person ?l - level)
    (reached ?p - person)
    (door_open ?l - level)
    (adjacent_up ?from ?to - level)
    (adjacent_down ?from ?to - level)
    (lift_count ?c - count)
    (next_count ?current ?next - count)
  )

  (:action move_up
    :parameters (?from ?to - level)
    :precondition (and (elevator_at ?from) (adjacent_up ?from ?to)
                       (not (door_open ?from)))
    :effect (and (not (elevator_at ?from)) (elevator_at ?to))
  )

  (:action move_down
    :parameters (?from ?to - level)
    :precondition (and (elevator_at ?from) (adjacent_down ?from ?to)
                       (not (door_open ?from)))
    :effect (and (not (elevator_at ?from)) (elevator_at ?to))
  )

  (:action open_door
    :parameters (?l - level)
    :precondition (and (elevator_at ?l) (not (door_open ?l)))
    :effect (and (door_open ?l))
  )

  (:action close_door
    :parameters (?l - level)
    :precondition (and (elevator_at ?l) (door_open ?l))
    :effect (and (not (door_open ?l)))
  )

  (:action load
    :parameters (?p - person ?l - level ?current ?next - count)
    :precondition (and 
      (person_at ?p ?l)
      (elevator_at ?l)
      (door_open ?l)
      (lift_count ?current)
      (next_count ?current ?next)
      (not (reached ?p))
    )
    :effect (and
      (person_in_elevator ?p)
      (not (person_at ?p ?l))
      (lift_count ?next)
      (not (lift_count ?current))
    )
  )

  (:action unload
    :parameters (?p - person ?l - level ?previous ?current - count)
    :precondition (and
      (person_in_elevator ?p)
      (elevator_at ?l)
      (door_open ?l)
      (lift_count ?current)
      (next_count ?previous ?current)
      (destination ?p ?l)
    )
    :effect (and
      (person_at ?p ?l)
      (not (person_in_elevator ?p))
      (lift_count ?previous)
      (not (lift_count ?current))
      (reached ?p)
    )
  )
)
"""

# COPY-FLAG-3-END


def generate_capacity_pddl_domain(output_file="elevator_domain_capacity.pddl"):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(pddl_domain_capacity)


# COPY-FLAG-4-START

def generate_capacity_pddl_from_config(config, output_file):
    validate_capacity_config(config)
    num_levels = config["num_levels"]
    elevator_start = config["elevator_start"]
    capacity = config["capacity"]
    requests = config["requests"]
    persons = [f"person{i + 1}" for i in range(len(requests))]
    counts = [f"c{i}" for i in range(capacity + 1)]

    pddl = "(define (problem elevator_capacity_problem)\n"
    pddl += "  (:domain elevator)\n"
    pddl += "  (:objects\n"
    pddl += f"    {' '.join(f'level{i}' for i in range(num_levels))} - level\n"
    if persons:
        pddl += f"    {' '.join(persons)} - person\n"
    pddl += f"    {' '.join(counts)} - count\n  )\n\n"

    pddl += f"  (:init\n    (elevator_at level{elevator_start})\n    (lift_count c0)\n"
    for floor in range(num_levels - 1):
        pddl += f"    (adjacent_up level{floor} level{floor + 1})\n"
        pddl += f"    (adjacent_down level{floor + 1} level{floor})\n"
    for count in range(capacity):
        pddl += f"    (next_count c{count} c{count + 1})\n"
    for person, (start, goal) in zip(persons, requests):
        pddl += f"    (person_at {person} level{start})\n"
        pddl += f"    (destination {person} level{goal})\n"
        if start == goal:
            pddl += f"    (reached {person})\n"
    pddl += "  )\n\n  (:goal\n    (and\n"
    for person in persons:
        pddl += f"      (reached {person})\n"
    pddl += "    )\n  )\n)"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(pddl)
    return pddl


# COPY-FLAG-4-END
