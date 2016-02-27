import sys

sys.path.append('../hmm')
import hmm

'''Sample data taken from
http://homepages.ulb.ac.be/~dgonze/TEACHING/viterbi.pdf'''

def make_model():
    model = hmm.HiddenMarkovModel()

    h = 'H'
    l = 'L'

    model.add_initial_state(h, 0.5)
    model.add_initial_state(l, 0.5)

    model.add_transition(h, l, 0.5)
    model.add_transition(h, h, 0.5)
    model.add_transition(l, l, 0.6)
    model.add_transition(l, h, 0.4)

    model.add_emission(h, 'A', 0.2)
    model.add_emission(h, 'C', 0.3)
    model.add_emission(h, 'G', 0.3)
    model.add_emission(h, 'T', 0.2)

    model.add_emission(l, 'A', 0.3)
    model.add_emission(l, 'C', 0.2)
    model.add_emission(l, 'G', 0.2)
    model.add_emission(l, 'T', 0.3)

    return model
