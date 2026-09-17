(define (problem elevator_capacity_problem)
  (:domain elevator)
  (:objects
    level0 level1 level2 level3 level4 level5 - level
    c0 c1 c2 c3 c4 - count
  )

  (:init
    (elevator_at level5)
    (lift_count c0)
    (adjacent_up level0 level1)
    (adjacent_down level1 level0)
    (adjacent_up level1 level2)
    (adjacent_down level2 level1)
    (adjacent_up level2 level3)
    (adjacent_down level3 level2)
    (adjacent_up level3 level4)
    (adjacent_down level4 level3)
    (adjacent_up level4 level5)
    (adjacent_down level5 level4)
    (next_count c0 c1)
    (next_count c1 c2)
    (next_count c2 c3)
    (next_count c3 c4)
  )

  (:goal
    (and
    )
  )
)