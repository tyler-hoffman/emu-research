#! /usr/bin/env python3

import math
from toyexample import make_model

model = make_model()

observed = 'GGCACTGAA'

expected_sequence = list('HHHLLLLLL')
expected_probability = 2 ** -24.49

computed_sequence, computed_probability = model.viterbi(list(observed))

was_correct = computed_sequence == expected_sequence
probability_error = ((expected_probability - computed_probability) / expected_probability)

if was_correct and probability_error < 0.001:
    print('pass')
else:
    print('fail')
