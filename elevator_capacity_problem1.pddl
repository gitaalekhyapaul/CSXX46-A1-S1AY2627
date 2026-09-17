(define (problem elevator_capacity_problem)
  (:domain elevator)
  (:objects
    level0 level1 level2 level3 - level
    person1 person2 - person
    c0 c1 - count
  )

  (:init
    (elevator_at level0)
    (lift_count c0)
    (adjacent_up level0 level1)
    (adjacent_down level1 level0)
    (adjacent_up level1 level2)
    (adjacent_down level2 level1)
    (adjacent_up level2 level3)
    (adjacent_down level3 level2)
    (next_count c0 c1)
    (person_at person1 level3)
    (destination person1 level0)
    (person_at person2 level1)
    (destination person2 level2)
  )

  (:goal
    (and
      (reached person1)
      (reached person2)
    )
  )
)