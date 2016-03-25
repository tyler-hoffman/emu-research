import random

class HiddenMarkovModel:
    '''Hidden Markov Model'''

    def __init__(self, pi = None, a = None, b = None):
        self.initial_states = ProbabilityPair()
        self.state_map = {}
        self.possible_observations = set()
        self.current_state = None

        if pi:
            for label, probability in pi.items():
                self.add_initial_state(label, probability)
        if a:
            for (from_label, to_label), prob in a.items():
                self.add_transition(from_label, to_label, prob)
        if b:
            for (state, obs), prob in b.items():
                self.add_emission(state, obs, prob)

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

    def get_sequence(self, terminate = lambda i, x: not x):

        if type(terminate) is int:
            f = lambda i, x: not x or i >= terminate
        else:
            f = terminate

        self.current_state = None
        output = []
        i = 0
        while True:
            token = self.next()
            if f(i, token):
                return output
            else:
                output.append(token)
                i += 1

        return output
        #return [self.next() for i in range(length)]

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

        for t in range(0, len(observed) - 1):
            next_steps = {label: 0 for label in self.state_map}

            for label, state in self.state_map.items():
                for (to_state, prob) in state.transitions:
                    next_steps[to_state.element] += prob * table[t][label]

            for label, total in next_steps.items():
                rate = self.state_map[label].emit_rate(observed[t + 1])
                table[t + 1][label] = rate * total

        return table

    def backward(self, observed):
        length = len(observed)
        table = [{} for o in observed]

        for s in self.state_map:
            table[length - 1][s] = 1

        for t in range(length - 2, -1, -1):
            for from_label, from_state in self.state_map.items():
                summation = 0
                summation1 = 0
                for (to_state, prob) in from_state.transitions:
                    to_label = to_state.element
                    summation1 += (from_state.transition_rate(to_state)
                            * to_state.emit_rate(observed[t + 1])
                            * table[t + 1][to_label])
                table[t][from_label] = summation1
                for to_label, to_state in self.state_map.items():
                    summation += (from_state.transition_rate(to_state)
                            * to_state.emit_rate(observed[t + 1])
                            * table[t + 1][to_label])
                table[t][from_label] = summation

        return table

    def probability_of_observed(self, observed, forward_table = None):
        if not forward_table:
            forward_table = self.forward(observed)
        return sum(forward_table[-1].values())

    def probability_of_transition_at_time(self, from_label, to_label, t, forward_table, backward_table, observation_probability, observed):
        return (forward_table[t][from_label]
                * self.transition_probability(from_label, to_label)
                * self.state_map[to_label].emit_rate(observed[t + 1])
                * backward_table[t + 1][to_label]
                / observation_probability)

    def probability_of_state_at_time(self, label, t, forward_table, backward_table, observation_probability, observed):
        prob = 0
        for to_label in self.state_map:
            prob += self.probability_of_transition_at_time(label, to_label, t, forward_table, backward_table, observation_probability, observed)
        return prob

    def baum_welsch(self, observed):
        forward_table = self.forward(observed)
        backward_table = self.backward(observed)
        observation_probability = self.probability_of_observed(observed, forward_table)

        #def probability_of_transition_at_time(from_label, to_label, t):
        #    return (forward_table[t][from_label]
        #            * self.transition_probability(from_label, to_label)
        #            * self.state_map[to_label].emit_rate(observed[t + 1])
        #            * backward_table[t + 1][to_label]
        #            / observation_probability)

        #def probability_of_state_at_time(label, t):
        #    prob = 0
        #    for to_label in self.state_map:
        #        prob += probability_of_transition_at_time(label, to_label, t, forward_table, backward_table, observation_probability, observed)
        #    return prob

        transition_table = {}
        for from_state in self.state_map:
            for (state, _) in self.state_map[from_state].transitions:
                to_state = state.element

                key = (from_state, to_state)
                transition_table[key] = []
                for t in range(len(observed) - 1):
                    transition_table[key].append(self.probability_of_transition_at_time(
                            from_state, to_state, t, forward_table, backward_table, observation_probability, observed))

        # memoize probability of state at given times
        probability_at_times = {}
        for state in self.state_map:
            for t in range(len(observed) - 1):
                probability_at_times[(state, t)] = self.probability_of_state_at_time(state, t, forward_table, backward_table, observation_probability, observed)

        transition_out_table = {}
        #TODO: speed this up
        for state in self.state_map:
            transition_out_table[state] = []
            for t in range(len(observed) - 1):
                transition_out_table[state].append(probability_at_times[(state, t)])
            transition_out_table[state].append(
                    forward_table[-1][state] / observation_probability)

        expected_transitions = {}
        for state in self.state_map:
            prob = 0
            for t in range(len(observed) - 1):
                prob += probability_at_times[(state, t)]#self.probability_of_state_at_time(state, t, forward_table, backward_table, observation_probability, observed)
            expected_transitions[state] = prob

        expected_transitions = {k: sum(v) for k, v in transition_table.items()}
        expected_transitions_out = {k: sum(v[:-1]) for k, v in transition_out_table.items()}

        pi_bar = {}
        for state in self.state_map:
            pi_bar[state] = transition_out_table[state][0]


        a_bar = {}
        for from_state, state in self.state_map.items():
            for to_state2, prob in state.transitions:
                to_state = to_state2.element
            #for to_state in self.state_map:
                key = (from_state, to_state)

                if expected_transitions[key]:
                    a_bar[key] = expected_transitions[key] / expected_transitions_out[from_state]
                else:
                    a_bar[key] = 0

        b_bar = {}
        for state in self.state_map:
            for emission in self.possible_observations:
                label = (state, emission)
                numerator = 0
                denominator = 0
                # TODO: Fix this line
                for t in range(len(observed)):
                    obs = observed[t]
                    denominator += transition_out_table[state][t]
                    if emission == obs:
                        numerator += transition_out_table[state][t]
                b_bar[label] = numerator / denominator

        if True:
            return pi_bar, a_bar, b_bar

        model = HiddenMarkovModel()
        for label, probability in pi_bar.items():
            model.add_initial_state(label, probability)

        for (from_label, to_label), prob in a_bar.items():
            model.add_transition(from_label, to_label, prob)

        for (state, obs), prob in b_bar.items():
            model.add_emission(state, obs, prob)

        #ßmodel.normalize()

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

class ProbIterator:
    def __init__(self, prob_pair):
        self.prob_pair = prob_pair
        self.current = 0

    def __next__(self):

        prob_pair = self.prob_pair
        if self.current == len(prob_pair.elements):
            raise StopIteration
        else:
            self.current += 1
            element = prob_pair.elements[self.current - 1]
            return (element, prob_pair.probability(element))

class ProbabilityPair:

    def __init__(self):
        self.elements = []
        self.probabilities = []

    def __repr__(self):
        return str(['{}({})'.format(e, p) for e, p in zip(self.elements, self.probabilities)])

    def __iter__(self):
        return ProbIterator(self)

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
