(define (problem elevator_problem)
  (:domain elevator)
  (:objects
    level0 level1 level2 level3 level4 - level
    person1 person2 person3 person4 - person
  )

  (:init
    (elevator_at level2)
    (elevator_empty)
    (person_at person1 level0)
    (person_at person2 level4)
    (person_at person3 level2)
    (person_at person4 level4)
    (adjacent_up level0 level1)
    (adjacent_down level1 level0)
    (adjacent_up level1 level2)
    (adjacent_down level2 level1)
    (adjacent_up level2 level3)
    (adjacent_down level3 level2)
    (adjacent_up level3 level4)
    (adjacent_down level4 level3)
  )

  (:goal
    (and
      (person_at person1 level4)
      (person_at person2 level1)
      (person_at person3 level2)
      (person_at person4 level0)
    )
  )
)