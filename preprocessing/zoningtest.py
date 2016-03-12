#! /usr/bin/env python3
import sys
sys.path.append('../hmm')

from trainer import train
from hmm import HiddenMarkovModel

def make_model(states = 10, outputs = 5):
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

def get_data_sets(filename):
    sets = {}
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip().split(' ')
            label = line[0]
            data = line[1:]
            if label in sets:
                sets[label].append([int(x) for x in data])
            else:
                sets[label] = [[int(x) for x in data]]

    return sets

if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        print('use: ./zoningtest.py <datafile>')
    else:
        filename = argv[1]
        data = get_data_sets(filename)

        hmms = {}

        for label in data:
            hmms[label] = make_model(14, 8)

        print('training')
        for label in hmms:
            model = hmms[label]
            data_set = data[label]
            epochs = 3

            hmms[label] = train(model, data_set, epochs, lambda x: None)
        print('training complete\n')

        count = 0
        correct = 0

        for label, data_set in data.items():

            for observed in data_set:
                best_label = None
                max_prob = 0

                for name, model in hmms.items():
                    prob = model.probability_of_observed(observed)

                    if prob > max_prob:
                        max_prob = prob
                        best_label = name

                print('{}: {}'.format(label, best_label))
                count += 1
                if label == best_label:
                    correct += 1
        print('success rate: {0:.1f}%'.format(100 * correct / count))
