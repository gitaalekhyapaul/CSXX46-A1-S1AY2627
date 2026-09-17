(define (problem elevator_problem)
  (:domain elevator)
  (:objects
    level0 level1 level2 - level
    person1 - person
  )

  (:init
    (elevator_at level0)
    (elevator_empty)
    (person_at person1 level2)
    (adjacent_up level0 level1)
    (adjacent_down level1 level0)
    (adjacent_up level1 level2)
    (adjacent_down level2 level1)
  )

  (:goal
    (and
      (person_at person1 level0)
    )
  )
)