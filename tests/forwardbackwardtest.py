#! /usr/bin/env python3

from toyexample import make_model

model = make_model()

expected = 0.0038432
computed = model.probability_of_observed(list('GGCA'))
error = abs((expected - computed) / expected)

print('error: {}'.format(error))
if error < 0.001:
    print('pass')
else:
    print('fail')
