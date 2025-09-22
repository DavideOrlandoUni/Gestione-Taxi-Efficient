
(define (problem taxi-case1)
  (:domain taxi-planner)
  (:objects
    taxi1 - taxi
    p1 - passenger
    st l1 - location
  )
  (:init
    (station st)
    (at taxi1 st)
    (passenger-at p1 l1)
  )
  (:goal (and
    (passenger-at p1 st)
  ))
)
