import random

class HiddenMarkovModel:
    '''Hidden Markov Model'''

    def __init__(self):
        self.initial_states = ProbabilityPair()
        self.state_map = {}
        self.possible_observations = set()
        self.current_state = None

    def add_initial_state(self, element, probability):
        state = self.get_state(element)
        self.initial_states.add(state, probability)

    def add_transition(self, from_element, to_element, probability):
        self.get_state(from_element).add_transition(
                self.get_state(to_element), probability)

    def add_emission(self, state, emission, probability):
        self.get_state(state).add_emission(emission, probability)
        self.possible_observations.add(emission)

    def get_state(self, element):
        if element in self.state_map:
            return self.state_map[element]
        else:
            state = State(element)
            self.state_map[element] = state
            return state

    def normalize(self):
        for state in self.state_map.values():
            state.emissions.normalize()
            state.transitions.normalize()
        self.initial_states.normalize()

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
        return self.get_state(from_element).transition_rate(
                self.get_state(to_element))

    def forward(self, observed):
        table = [{} for o in observed]
        states = self.state_map.keys()
        for s in states:
            state = self.get_state(s)
            initial_rate = self.initial_states.probability(state)
            emit_rate = state.emit_rate(observed[0])
            table[0][s] = initial_rate * emit_rate

        for t in range(1, len(observed)):
            for label, state in self.state_map.items():
                emit_rate = state.emit_rate(observed[t])
                summation = 0
                for from_label, from_state in self.state_map.items():
                    summation += (table[t - 1][from_label]
                            * from_state.transition_rate(state))
                table[t][label] = summation * emit_rate

        return table

    def backward(self, observed):
        length = len(observed)
        table = [{} for o in observed]

        for s in self.state_map:
            table[length - 1][s] = 1

        for t in range(length - 2, -1, -1):
            for from_label, from_state in self.state_map.items():
                summation = 0
                for to_label, to_state in self.state_map.items():
                    summation += (from_state.transition_rate(to_state)
                            * to_state.emit_rate(observed[t + 1])
                            * table[t + 1][to_label])
                table[t][from_label] = summation

        return table

    def probability_of_observed(self, observed, forward_table = None):

        if not forward_table:
            forward_table = self.forward(observed)

        final_col = forward_table[-1]
        prob = 0
        for p in final_col.values():
            prob += p

        return prob

    def baum_welsch(self, observed):
        forward_table = self.forward(observed)
        backward_table = self.backward(observed)
        observation_probability = self.probability_of_observed(observed, forward_table)
        print('--- {}'.format(observation_probability))
        def probability_of_transition_at_time(from_label, to_label, t):
            print('; {}, {}'.format(t, from_label))
            print(forward_table[t])
            print(forward_table[t][from_label])
            return (forward_table[t][from_label]
                    * self.transition_probability(from_label, to_label)
                    * self.state_map[to_label].emit_rate(observed[t + 1])
                    * backward_table[t + 1][to_label]
                    / observation_probability)

        def probability_of_state_at_time(label, t):
            prob = 0
            for to_label in self.state_map:
                prob += probability_of_transition_at_time(label, to_label, t)
            return prob

        transition_table = [{} for i in range(len(observed) - 1)]
        for t in range(len(observed) - 1):
            for from_state in self.state_map:
                for to_state in self.state_map:
                    transition_table[t][(from_state, to_state)] = probability_of_transition_at_time(
                            from_state, to_state, t)
            #from_label = observed[t]
            #to_label = observed[t + 1]
            #transition_table[t][(to_label, from_label)] = probability_of_transition_at_time(
            #        to_label, from_label, t)


        probability_table = [{} for o in observed]
        for t in range(len(observed)):
            label = observed[t]
            probability_table[t][label] = probability_of_state_at_time(label, t)

        pi_bar = {}
        for label in self.state_map:
            pi_bar[label] = probability_table[0][label]

        a_bar = {}
        for state in self.state_map:
            a_bar[state] = {}
            denominator = 0

            for t in len(probability_table):
                denominator += probability_table[t][state]

            for to_state in self.state_map:
                numerator = 0
                for t in len(transition_table):
                    numerator += transition_table[t][(state, to_state)]
                a_bar[state][to_state] = numerator / denominator

        b_bar = {}
        for state in self.state_map:
            b_bar[state] = {}
            for observation in self.possible_observations:
                numerator = 0
                denominator = 0

                for t in range(len(observed)):
                    if observed[t] == observation:
                        numerator += probability_table[t][state]
                    denominator += probability_table[t][state]

                b_bar[state][observation] = numerator / denominator

        print(a_bar)

        # This isn't so good
        model = HiddenMarkovModel()
        for label, probability in pi_bar:
            model.add_initial_state(label, probability)

        for from_label, stuff in a_bar.items():
            for to_label, p in stuff.items():
                model.add_transition(from_label, to_label, p)

        for state, stuff in b_bar.items():
            for label, p in stuff:
                model.add_emission(state, label, p)

        model.normalize()

        return model


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

def update_probabilities(probability_pair, probs):
    probability_pair.clear()
    for label, probability in probs.items():
        probability_pair.add(label, probability)

class ProbabilityPair:

    def __init__(self):
        self.elements = []
        self.probabilities = []

    def clear(self):
        self.__init__()

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

    def normalize(self):
        total = self.get_total_probability()
        self.probabilities = [p / total for p in self.probabilities]
