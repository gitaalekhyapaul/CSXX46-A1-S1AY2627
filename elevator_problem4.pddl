(define (problem elevator_problem)
  (:domain elevator)
  (:objects
    level0 - level
    person1 person2 - person
  )

  (:init
    (elevator_at level0)
    (elevator_empty)
    (person_at person1 level0)
    (person_at person2 level0)
  )

  (:goal
    (and
      (person_at person1 level0)
      (person_at person2 level0)
    )
  )
)