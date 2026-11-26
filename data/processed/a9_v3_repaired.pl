

blocked(U) :- exception_of(_, U).
holds(U)   :- in_force(U), not blocked(U).
