(define (problem elevator_problem)
  (:domain elevator)
  (:objects
    level0 level1 level2 level3 - level
  )

  (:init
    (elevator_at level3)
    (elevator_empty)
    (adjacent_up level0 level1)
    (adjacent_down level1 level0)
    (adjacent_up level1 level2)
    (adjacent_down level2 level1)
    (adjacent_up level2 level3)
    (adjacent_down level3 level2)
  )

  (:goal
    (and
    )
  )
)