#! /usr/bin/env python3

import json
from hmm.hmm import HiddenMarkovModel, State, ProbabilityPair

def prob_pair_to_dict(prob_pair, to_element = lambda x: x):
    return [(to_element(state), prob) for state, prob in prob_pair]

def dict_to_prob_pair(data, to_element = lambda x: x):
    output = ProbabilityPair()
    prev = 0
    for e, p in zip(data['elements'], data['probabilities']):
        p -= prev
        output.add(to_element(e), p)
        prev += p
    return output

def state_to_dict(state):
    return {
        'element': state.element.element,
        'transitions': prob_pair_to_dict(state.transitions),
        'emissions': prob_pair_to_dict(state.emissions.to_dict)
    }

def dict_to_state(data):
    output = State(data['element'])
    #output.transitions = dict_to_prob_pair(data['transitions'])
    #output.emissions = dict_to_prob_pair(data['emissions'])
    return output

initial_states = 'initial_states'
emissions = 'emissions'
transitions = 'transitions'

def hmm_to_dict(hmm):

    get_element = lambda x: x.element
    output = {
        initial_states: prob_pair_to_dict(hmm.initial_states, get_element),
        transitions: {}
    }

    # transitions
    for from_state in hmm.state_map.values():
        trans = prob_pair_to_dict(from_state.transitions, get_element)
        emit = prob_pair_to_dict(from_state.emissions, int)
        output[transitions][from_state.element] = (trans, emit)

    return output

def dict_to_hmm(data):
    output = HiddenMarkovModel()
    for (element, prob) in data[initial_states]:
        output.add_initial_state(element, prob)

    for from_state, (trans, emit) in data[transitions].items():
        for (to_state, prob) in trans:
            output.add_transition(int(from_state), int(to_state), prob)
        for (e, prob) in emit:
            output.add_emission(int(from_state), int(e), prob)


    return output

def save(models, filename):
    data = {label: hmm_to_dict(model) for label, model in models}
    json.dump(data, open(filename, 'w'))

def load(filename):
    data = json.load(open(filename))
    return {int(label): dict_to_hmm(model) for label, model in data.items()}
