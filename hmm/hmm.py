import random

class HiddenMarkovModel:
    '''Hidden Markov Model'''

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

    def transition_probability(self, from_element, to_element):
        return self.get_state(from_element).transition_probability(
                self.get_state(to_element))

    def forward(self, observed):
        table = []
        states = self.state_map.keys()
        table.append({})
        for s in states:
            state = self.get_state(s)
            initial_rate = self.initial_states.probability(state)
            emit_rate = state.emit_rate(observed[0])
            table[0][s] = initial_rate * emit_rate

        for t in range(1, len(observed)):
            table.append({})
            for to_s in states:
                to_state = self.get_state(to_s)
                emit_rate = to_state.emit_rate(observed[t])
                summation = 0
                for from_s in self.state_map.keys():
                    from_state = self.get_state(from_s)
                    summation += table[t - 1][from_s] * from_state.transition_rate(to_state)
                table[t][to_s] = summation * emit_rate

        return table

    def backward(self, observed):
        length = len(observed)
        table = [{} for i in range(length)]
        states = self.state_map.keys()

        for s in states:
            table[length - 1][s] = 1 / len(states)

        for t in range(length - 2, -1, -1):
            for from_s in states:
                from_state = self.get_state(from_s)
                summation = 0
                for to_s in states:
                    to_state = self.get_state(to_s)
                    summation += (from_state.transition_rate(to_state)
                            * to_state.emit_rate(observed[t + 1])
                            * table[t + 1][to_s])
                table[t][from_s] = summation

        return table

    def viterbi(self, observations):
        '''Do the viterbi algorithm
        Computes the most likely sequence and its probability

        observations -- list of observed outputs
        '''

        length = len(observations)

        backtrace = [{} for i in range(length)]
        probability = [{} for i in range(length)]
        last = None

        # base case
        for label, state in self.state_map.items():
            probability[0][label] = (self.initial_states.probability(state)
                    * state.emit_rate(observations[0]))
            backtrace[0][label] = None

        # recursive step
        for t in range(1, length):
            for label, state in self.state_map.items():
                max_prob = 0
                max_label = None

                for from_label, from_state in self.state_map.items():
                    prob = (probability[t - 1][from_label]
                            * from_state.transition_rate(state))

                    if prob > max_prob:
                        max_prob = prob
                        max_label = from_label

                probability[t][label] = (max_prob
                        * state.emit_rate(observations[t]))
                backtrace[t][label] = max_label

        # figure out max probability and the last label
        max_prob = 0
        max_label = None
        for label in probability[length - 1]:
            p = probability[length - 1][label]
            if p > max_prob:
                max_prob = p
                max_label = label

        # backtrack through labels
        backwards = []
        current = max_label
        for t in range(length - 1, -1, -1):
            backwards.append(current)
            current = backtrace[t][current]

        # return the reversed backtrace and its probability
        return backwards[::-1], max_prob


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

    def transition_rate(self, to_state):
        return self.transitions.probability(to_state)

    def emit_rate(self, emission):
        return self.emissions.probability(emission)


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

    def probability(self, element):
        p = self.probabilities
        for i in range(len(self.elements)):
            if self.elements[i] == element:
                return p[0] if i == 0 else p[i] - p[i - 1]
        return 0

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
