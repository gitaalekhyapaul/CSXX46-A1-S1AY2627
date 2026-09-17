
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
