import random

class HiddenMarkovModel:

    def __init__(self):
        self.initial_states = ProbabilityPair()
        self.state_map = {}
        self.current_state = None

    def add_initial_state(self, element, probability):
        state = self.get_state(element)
        self.initial_states.add(state, probability)

    def add_transition(self, from_element, to_element, probability):
        self.get_state(from_element).add_transition(
                self.get_state(to_element), probability)

    def add_emission(self, state, emission, probability):
        self.get_state(state).add_emission(emission, probability)

    def get_state(self, element):
        if element in self.state_map:
            return self.state_map[element]
        else:
            state = State(element)
            self.state_map[element] = state
            return state

    def next(self):
        if self.current_state:
            self.current_state = self.current_state.transition()
        else:
            self.current_state = self.initial_states.get_random()
        return self.current_state.emit()

    def has_next(self):
        return (self.current_state and not self.initial_states.is_empty()
                or self.current_state and self.current_state.transitions_count > 1)

class State:

    def __init__(self, element):
        self.element = element
        self.transitions = ProbabilityPair()
        self.emissions = ProbabilityPair()

    def __repr__(self):
        return 'State({})'.format(self.element)

    def add_emission(self, symbol, probability):
        self.emissions.add(symbol, probability)

    def get_element(self):
        return self.element

    def add_transition(self, state, probability):
        self.transitions.add(state, probability)

    def emit(self):
        return self.emissions.get_random()

    def transition(self):
        return self.transitions.get_random()

    def transitions_count(self):
        return self.transitions.size()

    def emission_count(self):
        return self.emissions.size()


class ProbabilityPair:

    def __init__(self):
        self.elements = []
        self.probabilities = []

    def add(self, element, probability):
        probability += self.get_total_probability()
        self.elements.append(element)
        self.probabilities.append(probability)

    def size(self):
        return len(self.elements)

    def is_empty(self):
        return self.size() == 0

    def get_total_probability(self):
        if self.is_empty():
            return 0
        else:
            return self.probabilities[-1]

    def get_random(self):
        if not self.is_empty():
            elements = self.elements
            probabilities = self.probabilities

            r = random.random() * self.get_total_probability()
            begin = 0
            end = self.size()

            while begin < end:
                mid = (begin + end) // 2
                if r > probabilities[mid]:
                    begin = mid + 1
                elif r < probabilities[mid] and mid == 0 or r > probabilities[mid - 1]:
                    return elements[mid]
                else:
                    end = mid
