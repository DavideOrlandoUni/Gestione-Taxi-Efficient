
(define (problem taxi-case2)
  (:domain taxi-planner)
  (:objects
    taxi1 - taxi
    p1 p2 - passenger
    st l1 l2 - location
  )
  (:init
    (station st)
    (at taxi1 st)
    (passenger-at p1 l1)
    (passenger-at p2 l2)
  )
  (:goal (and
    (passenger-at p1 st)
    (passenger-at p2 st)
  ))
)
