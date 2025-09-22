
(define (problem taxi-case3)
  (:domain taxi-planner)
  (:objects
    taxi1 - taxi
    p1 p2 p3 - passenger
    st l1 l2 l3 - location
  )
  (:init
    (station st)
    (at taxi1 st)
    (passenger-at p1 l1)
    (passenger-at p2 l2)
    (passenger-at p3 l3)
  )
  (:goal (and
    (passenger-at p1 st)
    (passenger-at p2 st)
    (passenger-at p3 st)
  ))
)
