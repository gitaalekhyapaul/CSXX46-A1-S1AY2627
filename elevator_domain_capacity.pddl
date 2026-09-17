
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
