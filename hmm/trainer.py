#! /usr/bin/env python3

from hmm.hmm import HiddenMarkovModel

def make_model(states = 8, outputs = 5):
    model = HiddenMarkovModel()

    for state in range(states):
        model.add_initial_state(state, 1 / states)
        for output in range(outputs):
            model.add_emission(state, output, 1 / outputs)

    for state in range(states):
        for to_state in range(states):
            model.add_transition(state, to_state, 1 / states)

    model.normalize()
    return model

def make_2d_model(width, height, max_jump, outputs = 5):
    model = HiddenMarkovModel()

    model.add_initial_state(0, 1)
    states = width * height
    for state in range(states):
        for output in range(outputs):
            model.add_emission(state, output, 1 / outputs)

    for row in range(height):
        for col in range(width):
            state = row * width + col
            for i in range(row, min(height, row + max_jump + 1)):
                model.add_transition(state, i * width + col, 1)
            for i in range(col, min(width, col + max_jump + 1)):
                model.add_transition(state, row * width + i, 1)

    model.normalize()
    return model

def make_linear_model(states = 25, outputs = 5):
    model = HiddenMarkovModel()

    for state in range(states):
        model.add_initial_state(state, 1 / states)
        for output in range(outputs):
            model.add_emission(state, output, 1 / outputs)

    for state in range(states):
        for to_state in range(state, min(states, state + 3)):
            model.add_transition(state, to_state, 1 / states)

    model.normalize()
    return model


def train(model, sequences, epochs = 1, callback = None):

    def merge(dest, source):
        for label in dest:
            dest[label] = dest[label] + source[label]

    for i in range(epochs):
        if callback:
            callback(i)
        print(i)
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

def get_success_rate(label, data_sets, hmms):
    count = 0
    correct = 0

    for observed in data_sets:

        best_label = None
        max_prob = 0

        for name, model in hmms.items():
            prob = model.probability_of_observed(observed)

            if prob > max_prob:
                max_prob = prob
                best_label = name

        count += 1
        if label == best_label:
            correct += 1
    return correct, count
