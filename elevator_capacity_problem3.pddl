(define (problem elevator_capacity_problem)
  (:domain elevator)
  (:objects
    level0 - level
    person1 person2 - person
    c0 c1 c2 c3 - count
  )

  (:init
    (elevator_at level0)
    (lift_count c0)
    (next_count c0 c1)
    (next_count c1 c2)
    (next_count c2 c3)
    (person_at person1 level0)
    (destination person1 level0)
    (reached person1)
    (person_at person2 level0)
    (destination person2 level0)
    (reached person2)
  )

  (:goal
    (and
      (reached person1)
      (reached person2)
    )
  )
)