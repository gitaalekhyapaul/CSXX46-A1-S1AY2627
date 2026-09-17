
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
      (elevator_at ?l)
      (person_at ?p ?l)
      (door_open ?l)
      (not (reached ?p))
      (lift_count ?current)
      (next_count ?current ?next)
    )
    :effect (and
      (not (person_at ?p ?l))
      (person_in_elevator ?p)
      (not (lift_count ?current))
      (lift_count ?next)
    )
  )

  (:action unload
    :parameters (?p - person ?l - level ?previous ?current - count)
    :precondition (and
      (elevator_at ?l)
      (person_in_elevator ?p)
      (door_open ?l)
      (destination ?p ?l)
      (lift_count ?current)
      (next_count ?previous ?current)
    )
    :effect (and
      (not (person_in_elevator ?p))
      (person_at ?p ?l)
      (reached ?p)
      (not (lift_count ?current))
      (lift_count ?previous)
    )
  )
)
