#! /usr/bin/env python3

import hmm

model = hmm.HiddenMarkovModel()
a = 'A'
b = 'B'

model.add_initial_state(a, 1)
model.add_initial_state(b, 10)

model.add_transition(a, a, 1)
model.add_transition(a, b, 1)
model.add_transition(b, a, 1)

model.add_emission(a, 'a', 1)
model.add_emission(a, 'abc', 1)
model.add_emission(b, 'b', 1)

sequence = [model.next() for i in range(10)]
print(sequence)
