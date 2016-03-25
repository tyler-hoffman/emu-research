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

model = hmm.HiddenMarkovModel()
healthy = 'Healthy'
fever = 'Fever'
normal = 'normal'
cold = 'cold'
dizzy = 'dizzy'
e = 'E'

model.add_initial_state(healthy, 0.6)
model.add_initial_state(fever, 0.4)

model.add_transition(healthy, healthy, 0.69)
model.add_transition(healthy, fever, 0.3)
model.add_transition(healthy, e, 0.01)
model.add_transition(fever, healthy, 0.4)
model.add_transition(fever, fever, 0.59)
model.add_transition(fever, e, 0.01)

model.add_emission(healthy, normal, 0.5)
model.add_emission(healthy, cold, 0.4)
model.add_emission(healthy, dizzy, 0.1)
model.add_emission(fever, normal, 0.1)
model.add_emission(fever, cold, 0.3)
model.add_emission(fever, dizzy, 0.6)

model.normalize()

observations = [normal, cold, dizzy]

print('p: {}'.format(model.probability_of_observed(observations)))
print('---')

print(model.forward(observations))
print('---')
print(model.backward(observations))
print('---')
path, prob = model.viterbi([dizzy, normal])
print(path)
print(prob)
# print(model.backward(observations))
