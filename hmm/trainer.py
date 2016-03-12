#! /usr/bin/env python3

from hmm import HiddenMarkovModel

def train(model, sequences, epochs = 1, callback = None):

    def merge(dest, source):
        for label in dest:
            dest[label] = dest[label] + source[label]

    for i in range(epochs):
        if callback:
            callback(i)

        pi = None
        a = None
        b = None
        j = 0
        for sequence in sequences:
            new_pi, new_a, new_b = model.baum_welsch(sequence)
            if not pi:
                pi = new_pi
                a = new_a
                b = new_b
            else:
                merge(pi, new_pi)
                merge(a, new_a)
                merge(b, new_b)
            j += 1

        model = HiddenMarkovModel(pi, a, b)
        model.normalize()

    return model
