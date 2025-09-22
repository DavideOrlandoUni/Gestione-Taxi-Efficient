
(define (problem taxi-case4)
  (:domain taxi-planner)
  (:objects
    taxi1 taxi2 - taxi
    p1 p2 p3 p4 p5 p6 p7 p8 p9 - passenger
    st l1 l2 l3 l4 l5 l6 l7 l8 l9 - location
  )
  (:init
    (station st)
    (at taxi1 st)
    (at taxi2 st)
    (passenger-at p1 l1)
    (passenger-at p2 l2)
    (passenger-at p3 l3)
    (passenger-at p4 l4)
    (passenger-at p5 l5)
    (passenger-at p6 l6)
    (passenger-at p7 l7)
    (passenger-at p8 l8)
    (passenger-at p9 l9)
  )
  (:goal (and
    (passenger-at p1 st)
    (passenger-at p2 st)
    (passenger-at p3 st)
    (passenger-at p4 st)
    (passenger-at p5 st)
    (passenger-at p6 st)
    (passenger-at p7 st)
    (passenger-at p8 st)
    (passenger-at p9 st)
  ))
)