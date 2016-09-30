flip_bit = lambda x: ~x & 1

class conditional_value(object):
    def __init__(self, state_variable, index, bit, target_value):
        self.state_variable = state_variable
        self.index = index
        self.bit = bit
        self.target_value = target_value

    def assert_condition_fulfilled(self, state):
        # tests whether or not the given condition is fulfilled given a state
        # variables
        assert ith_bit(state[self.state_variable][self.index], self.bit) == self.target_value

    def condition_fulfilled(self, state):
        # tests whether or not the given condition is fulfilled given a state
        # variables
        return ith_bit(state[self.state_variable][self.index], self.bit) == self.target_value

class conditional_equality(object):
    def __init__(self, state_variable, index, bit, target_state_variable, target_index, target_bit):
        self.state_variable = state_variable
        self.index = index
        self.bit = bit
        self.target_state_variable = target_state_variable
        self.target_index = target_index
        self.target_bit = target_bit

    def assert_condition_fulfilled(self, state):
        # tests whether or not the given condition is fulfilled given a state
        # variables
        v1 = state[self.state_variable][self.index]
        v2 = state[self.target_state_variable][self.target_index]
        assert ith_bit(v1, self.bit) == ith_bit(v2, self.target_bit)

    def condition_fulfilled(self, state):
        # tests whether or not the given condition is fulfilled given a state
        # variables
        v1 = state[self.state_variable][self.index]
        v2 = state[self.target_state_variable][self.target_index]
        return ith_bit(v1, self.bit) == ith_bit(v2, self.target_bit)

class conditional_flipped_equality(object):
    def __init__(self, state_variable, index, bit, target_state_variable, target_index, target_bit):
        self.state_variable = state_variable
        self.index = index
        self.bit = bit
        self.target_state_variable = target_state_variable
        self.target_index = target_index
        self.target_bit = target_bit

    def assert_condition_fulfilled(self, state):
        # tests whether or not the given condition is fulfilled given a state
        # variables
        v1 = state[self.state_variable][self.index]
        v2 = state[self.target_state_variable][self.target_index]
        assert ith_bit(v1, self.bit) == flip_bit(ith_bit(v2, self.target_bit))

    def condition_fulfilled(self, state):
        # tests whether or not the given condition is fulfilled given a state
        # variables
        v1 = state[self.state_variable][self.index]
        v2 = state[self.target_state_variable][self.target_index]
        return ith_bit(v1, self.bit) == flip_bit(ith_bit(v2, self.target_bit))

def ith_bit(n, i):
    # gets the ith bit of n
    bit = 1 << (i-1)
    return (n&bit)>>(i-1)

def first_round_conditions():
    # Sets up the conditions necessary to meet the first round equalities.
    # Conditions sourced from page 16 of Wang's original paper.
    conditions = []

    # a1
    a1 = conditional_equality("a", 1, 7, "b", 0, 7)
    conditions += [a1]

    # d1
    d11 = conditional_value("d", 1, 7, 0)
    d12 = conditional_equality("d", 1, 8, "a", 1, 8)
    d13 = conditional_equality("d", 1, 11, "a", 1, 11)
    conditions += [d11, d12, d13]

    # c1
    c11 = conditional_value("c", 1, 7, 1)
    c12 = conditional_value("c", 1, 8, 1)
    c13 = conditional_value("c", 1, 11, 0)
    c14 = conditional_equality("c", 1, 26, "d", 1, 26)
    conditions += [c11, c12, c13, c14]

    # b1
    b11 = conditional_value("b", 1, 7, 1)
    b12 = conditional_value("b", 1, 8, 0)
    b13 = conditional_value("b", 1, 11, 0)
    b14 = conditional_value("b", 1, 26, 0)
    conditions += [b11, b12, b13, b14]

    # a2
    a21 = conditional_value("a", 2, 8, 1)
    a22 = conditional_value("a", 2, 11, 1)
    a23 = conditional_value("a", 2, 26, 0)
    a24 = conditional_equality("a", 2, 14, "b", 1, 14)
    conditions += [a21, a22, a23, a24]

    # d2
    d21 = conditional_value("d", 2, 14, 0)
    d22 = conditional_equality("d", 2, 19, "a", 2, 19)
    d23 = conditional_equality("d", 2, 20, "a", 2, 20)
    d24 = conditional_equality("d", 2, 21, "a", 2, 21)
    d25 = conditional_equality("d", 2, 22, "a", 2, 22)
    d26 = conditional_value("d", 2, 26, 1)
    conditions += [d21, d22, d23, d24, d25, d26]

    # c2
    c21 = conditional_equality("c", 2, 13, "d", 2, 13)
    c22 = conditional_value("c", 2, 14, 0)
    c23 = conditional_equality("c", 2, 15, "d", 2, 15)
    c24 = conditional_value("c", 2, 19, 0)
    c25 = conditional_value("c", 2, 20, 0)
    c26 = conditional_value("c", 2, 21, 1)
    c27 = conditional_value("c", 2, 22, 0)
    conditions += [c21, c22, c23, c24, c25, c26, c27]

    # b2
    b21 = conditional_value("b", 2, 13, 1)
    b22 = conditional_value("b", 2, 14, 1)
    b23 = conditional_value("b", 2, 15, 0)
    b24 = conditional_equality("b", 2, 17, "c", 2, 17)
    b25 = conditional_value("b", 2, 19, 0)
    b26 = conditional_value("b", 2, 20, 0)
    b27 = conditional_value("b", 2, 21, 0)
    b28 = conditional_value("b", 2, 22, 0)
    conditions += [b21, b22, b23, b24, b25, b26, b27, b28]

    # a3
    a31 = conditional_value("a", 3, 13, 1)
    a32 = conditional_value("a", 3, 14, 1)
    a33 = conditional_value("a", 3, 15, 1)
    a34 = conditional_value("a", 3, 17, 0)
    a35 = conditional_value("a", 3, 19, 0)
    a36 = conditional_value("a", 3, 20, 0)
    a37 = conditional_value("a", 3, 21, 0)
    a38 = conditional_equality("a", 3, 23, "b", 2, 23)
    a39 = conditional_value("a", 3, 22, 1)
    a3a = conditional_equality("a", 3, 26, "b", 2, 26)
    conditions += [a31, a32, a33, a34, a35, a36, a37, a38, a39, a3a]

    # d3
    d31 = conditional_value("d", 3, 13, 1)
    d32 = conditional_value("d", 3, 14, 1)
    d33 = conditional_value("d", 3, 15, 1)
    d34 = conditional_value("d", 3, 17, 0)
    d35 = conditional_value("d", 3, 20, 0)
    d36 = conditional_value("d", 3, 21, 1)
    d37 = conditional_value("d", 3, 22, 1)
    d38 = conditional_value("d", 3, 23, 0)
    d39 = conditional_value("d", 3, 26, 1)
    d3a = conditional_equality("d", 3, 30, "a", 3, 30)
    conditions += [d31, d32, d33, d34, d35, d36, d37, d38, d39, d3a]

    # c3
    c31 = conditional_value("c", 3, 17, 1)
    c32 = conditional_value("c", 3, 20, 0)
    c33 = conditional_value("c", 3, 21, 0)
    c34 = conditional_value("c", 3, 22, 0)
    c35 = conditional_value("c", 3, 23, 0)
    c36 = conditional_value("c", 3, 26, 0)
    c37 = conditional_value("c", 3, 30, 1)
    c38 = conditional_equality("c", 3, 32, "d", 3, 32)
    conditions += [c31, c32, c33, c34, c35, c36, c37, c38]

    # b3
    b31 = conditional_value("b", 3, 20, 0)
    b32 = conditional_value("b", 3, 21, 1)
    b33 = conditional_value("b", 3, 22, 1)
    b34 = conditional_equality("b", 3, 23, "c", 3, 23)
    b35 = conditional_value("b", 3, 26, 1)
    b36 = conditional_value("b", 3, 30, 0)
    b37 = conditional_value("b", 3, 32, 0)
    conditions += [b31, b32, b33, b34, b35, b36, b37]

    # a4
    a41 = conditional_value("a", 4, 23, 0)
    a42 = conditional_value("a", 4, 26, 0)
    a43 = conditional_equality("a", 4, 27, "b", 3, 27)
    a44 = conditional_equality("a", 4, 29, "b", 3, 29)
    a45 = conditional_value("a", 4, 30, 1)
    a46 = conditional_value("a", 4, 32, 0)
    conditions += [a41, a42, a43, a44, a45, a46]

    # d4
    d41 = conditional_value("d", 4, 23, 0)
    d42 = conditional_value("d", 4, 26, 0)
    d43 = conditional_value("d", 4, 27, 1)
    d44 = conditional_value("d", 4, 29, 1)
    d45 = conditional_value("d", 4, 30, 0)
    d46 = conditional_value("d", 4, 32, 1)
    conditions += [d41, d42, d43, d44, d45, d46]

    # c4
    c41 = conditional_equality("c", 4, 19, "d", 4, 19)
    c42 = conditional_value("c", 4, 23, 1)
    c43 = conditional_value("c", 4, 26, 1)
    c44 = conditional_value("c", 4, 27, 0)
    c45 = conditional_value("c", 4, 29, 0)
    c46 = conditional_value("c", 4, 30, 0)
    conditions += [c41, c42, c43, c44, c45, c46]

    # b4
    b41 = conditional_value("b", 4, 19, 0)
    b42 = conditional_equality("b", 4, 26, "c", 4, 26)
    b43 = conditional_value("b", 4, 27, 1)
    b44 = conditional_value("b", 4, 29, 1)
    b45 = conditional_value("b", 4, 30, 0)
    conditions += [b41, b42, b43, b44, b45]

    return conditions

def second_round_conditions():
    # Sets up the conditions necessary to meet the second round equalities.
    # Conditions sourced from page 16 of Wang's original paper.
    conditions = []

    # a5
    a51 = conditional_equality("a", 5, 19, "c", 4, 19)
    a52 = conditional_value("a", 5, 26, 1)
    a53 = conditional_value("a", 5, 27, 0)
    a54 = conditional_value("a", 5, 29, 1)
    a55 = conditional_value("a", 5, 32, 1)
    conditions += [a51, a52, a53, a54, a55]

    # d5
    d51 = conditional_equality("d", 5, 19, "a", 5, 19)
    d52 = conditional_equality("d", 5, 26, "b", 4, 26)
    d53 = conditional_equality("d", 5, 27, "b", 4, 27)
    d54 = conditional_equality("d", 5, 29, "b", 4, 29)
    d55 = conditional_equality("d", 5, 32, "b", 4, 32)
    conditions += [d51, d52, d53, d54, d55]

    # The code to handle the below conditions isn't built yet.

    # c5
    c51 = conditional_equality("c", 5, 26, "d", 5, 26)
    c52 = conditional_equality("c", 5, 27, "d", 5, 27)
    c53 = conditional_equality("c", 5, 29, "d", 5, 29)
    c54 = conditional_equality("c", 5, 30, "d", 5, 30)
    c55 = conditional_equality("c", 5, 32, "d", 5, 32)
    #conditions += [c51]
    #conditions += [c51, c52, c53, c54, c55]

    # b5
    b51 = conditional_equality("b", 5, 29, "c", 5, 29)
    b52 = conditional_value("b", 5, 30, 1)
    b53 = conditional_value("b", 5, 32, 0)
    #conditions += [b51, b52, b53]

    # a6
    a61 = conditional_value("a", 6, 29, 1)
    a62 = conditional_value("a", 6, 32, 1)
    #conditions += [a61, a62]

    # d6
    d61 = conditional_equality("d", 6, 29, "b", 5, 29)
    #conditions += [d61]

    # c6
    c61 = conditional_equality("c", 6, 29, "d", 6, 29)
    c62 = conditional_flipped_equality("c", 6, 30, "d", 6, 30)
    c63 = conditional_flipped_equality("c", 6, 32, "d", 6, 32)
    #conditions += [c61, c62, c63]

    return conditions
