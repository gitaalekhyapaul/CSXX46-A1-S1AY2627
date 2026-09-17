(define (problem elevator_problem)
  (:domain elevator)
  (:objects
    level0 level1 level2 level3 - level
    person1 person2 person3 - person
  )

  (:init
    (elevator_at level0)
    (elevator_empty)
    (person_at person1 level3)
    (person_at person2 level3)
    (person_at person3 level1)
    (adjacent_up level0 level1)
    (adjacent_down level1 level0)
    (adjacent_up level1 level2)
    (adjacent_down level2 level1)
    (adjacent_up level2 level3)
    (adjacent_down level3 level2)
  )

  (:goal
    (and
      (person_at person1 level0)
      (person_at person2 level0)
      (person_at person3 level0)
    )
  )
)