(define (problem elevator_capacity_problem)
  (:domain elevator)
  (:objects
    level0 level1 level2 level3 level4 - level
    person1 person2 person3 - person
    c0 c1 c2 - count
  )

  (:init
    (elevator_at level3)
    (lift_count c0)
    (adjacent_up level0 level1)
    (adjacent_down level1 level0)
    (adjacent_up level1 level2)
    (adjacent_down level2 level1)
    (adjacent_up level2 level3)
    (adjacent_down level3 level2)
    (adjacent_up level3 level4)
    (adjacent_down level4 level3)
    (next_count c0 c1)
    (next_count c1 c2)
    (person_at person1 level1)
    (destination person1 level4)
    (person_at person2 level1)
    (destination person2 level0)
    (person_at person3 level3)
    (destination person3 level3)
    (reached person3)
  )

  (:goal
    (and
      (reached person1)
      (reached person2)
      (reached person3)
    )
  )
)