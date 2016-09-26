import md4
from os import urandom
from wangs_conditions import conditional_value, conditional_equality, conditional_flipped_equality
from array import array
from struct import pack, unpack

flip_bit = lambda x: ~x & 1

def md4_states(txt):
    MD = md4.MD4()
    MD.update(txt, padding = False)
    return MD.int_states

def md4_hash(txt):
    MD = md4.MD4()
    MD.update(txt)
    return MD.digest()

def update_for_equality(w, index, target_value):
    # Takes w (a value of ai, bi, ci, or di) and updates it so
    # the bit at index reflects the stated value
    shift_amount = index - 1
    current_value = ith_bit(w, index) # 1 if w has 1 in relevant bit, 0 otherwise
    to_xor = (current_value ^ target_value) << shift_amount # val to xor with w
    return w ^ to_xor

def update_ith_bit_to_match_jth_bit(x, i, y, j):
    # updates x so its ith bit matches ys ith bit
    yj = ith_bit(y, j)
    x = update_for_equality(x, i, yj)
    return x

def ith_bit(n, i):
    # gets the ith bit of n
    bit = 1 << (i-1)
    return (n&bit)>>(i-1)

def rot_add(s1, s2):
    s = s1 + s2
    if s & 0xffffffff != s:
        s = (s & 0xffffffff) + 1
    return s

def right_rotate(n, b):
    return ((n >> b) | ((n & 0xffffffff) << (32 - b))) & 0xffffffff

def left_rotate(n, b):
	return ((n << b) | ((n & 0xffffffff) >> (32 - b))) & 0xffffffff

def f(x, y, z): return (x & y) | (~x & z)
def g(x, y, z): return (x & y) | (x & z) | (y & z)
def h(x, y, z): return x ^ y ^ z

def f1_inv(a, s, a0, b0, c0, d0):
    return (right_rotate(a, s) - a0 - f(b0, c0, d0)) & 0xffffffff

def f2_inv(a, s, a0, b0, c0, d0):
    return (right_rotate(a, s) - a0 - g(b0, c0, d0) - 0x5a827999) & 0xffffffff

def f3_inv(a, s, a0, b0, c0, d0):
    return (right_rotate(a, s) - a0 - h(b0, c0, d0) - 0x6ed9eba1) & 0xffffffff

class md4_state(object):
    def __init__(self, msg):
        self.msg = msg
        self.state = md4_states(msg)

    def update_for_r1_conditions(self, conditions):
        for condition in conditions:
            self.update_for_conditional(condition)

    def update_for_r2_conditions(self, conditions):
        for condition in conditions:
            if condition.condition_fulfilled(self.state):
                pass
            else:
                if condition.state_variable == "a" and condition.index == 5:
                    self.update_m_for_r211(condition)
                elif condition.state_variable == "d" and condition.index == 5:
                    self.update_m_for_r221(condition)
                elif condition.state_variable == "c" and condition.index == 5:
                    self.update_m_for_r23(condition)

    def update_for_conditional(self, conditional):
        if isinstance(conditional, conditional_value):
            self.update_for_conditional_value(conditional)
        elif isinstance(conditional, conditional_equality):
            self.update_for_conditional_equality(conditional)
        elif isinstance(conditional, conditional_flipped_equality):
            self.update_for_conditional_flipped_equality(conditional)

    def update_for_conditional_value(self, conditional):
        var = conditional.state_variable
        index = conditional.index
        bit = conditional.bit
        target_value = conditional.target_value

        old_value = self.state[var][index]
        new_value = update_for_equality(old_value, bit, target_value)
        self.state[var][index] = new_value

    def update_for_conditional_equality(self, conditional):
        var = conditional.state_variable
        index = conditional.index
        bit = conditional.bit
        target_var = conditional.target_state_variable
        target_index = conditional.target_index
        target_bit = conditional.target_bit

        current_val = self.state[var][index]
        current_target_val = self.state[target_var][target_index]
        new_val = update_ith_bit_to_match_jth_bit(current_val, bit, current_target_val, target_bit)
        self.state[var][index] = new_val

    def update_for_conditional_flipped_equality(self, conditional):
        var = conditional.state_variable
        index = conditional.index
        bit = conditional.bit
        target_var = conditional.target_state_variable
        target_index = conditional.target_index
        target_bit = conditional.target_bit
        target_val = flip_bit(ith_bit(self.state[target_var][target_index], target_bit))
        current_val = self.state[var][index]
        new_val = update_for_equality(current_val, bit, target_val)
        self.state[var][index] = new_val

    def words_to_m(self, words):
        m = ""
        for word in words:
            m += pack("<I", word)
        return m

    def m_to_words(self, m):
         return [unpack("<I", m[4*i:4*(i+1)])[0] for i in range(16)]

    def update_m_for_r211(self, condition):
        words = self.m_to_words(self.msg)
        bit = condition.bit

        # update a1
        a1 = self.state["a"][1]
        current_val = ith_bit(a1, bit)
        target_val = flip_bit(current_val)
        a1 = update_for_equality(a1, bit, target_val)
        self.state["a"][1] = a1

        #self.msg = self.words_to_m(words)
        self.msg = self.derive_m_from_state()
        self.state = md4_states(self.msg)

    def update_m_for_r221(self, condition):
        words = self.m_to_words(self.msg)
        bit = condition.bit - 2

        # update a2
        a2 = self.state["a"][2]
        current_val = ith_bit(a2, bit)
        target_val = flip_bit(current_val)
        a2 = update_for_equality(a2, bit, target_val)
        self.state["a"][2] = a2

        #self.msg = self.words_to_m(words)
        self.msg = self.derive_m_from_state()
        self.state = md4_states(self.msg)

    def update_m_for_r22(self, condition):
        # updates m for round 2 second collisions (d5,i)
        words = self.m_to_words(self.msg)

        word_index = 4
        word = words[word_index]
        state_num = self.state["d"][5]
        target_bit = condition.bit

        if isinstance(condition, conditional_value):
            target_value = condition.target_value
        elif isinstance(condition, conditional_equality):
            target_num = self.state[condition.target_state_variable][condition.target_index]
            target_value = ith_bit(target_num, condition.target_bit)

        current_bit_val = ith_bit(state_num, target_bit)
        a2 = self.state["a"][2]

        if current_bit_val == 1 and target_value == 0:
            new_word = word - 2**(target_bit - 6)
            new_a2 = (a2 - 2**(target_bit-3)) & 0xffffffff

        if current_bit_val == 0 and target_value == 1:
            new_word = rot_add(word, 2**(target_bit - 6))
            new_a2 = rot_add(a2, 2**(target_bit - 3))

        words[word_index] = new_word
        print bin(new_word + 2**33)
        msg = self.words_to_m(words)
        self.msg = msg
        new_states = md4_states(msg)

        """print "target value: " + str(target_value)
        print "target bit: " + str(target_bit - 3)
        print bin(2**33 + 2**(target_bit - 3))
        print bin(a2 + 2**33)
        print bin(new_a2 + 2**33)
        print bin(new_states["a"][2] + 2**33)"""

        #assert new_states["a"][2] == new_a2

        self.state["a"][2] = new_a2

    def update_m_for_r23(self, condition):
        # updates m for round 2 third collisions (c5,i)
        i = condition.bit

        # print out stuff
        print "Target value is "+ str(ith_bit(self.state["d"][5], i))
        print "Target bit:      "+bin(2**33 + 2**(i-1))[2:]
        print "Current c value: "+bin(2**33 + self.state["c"][5])[2:]
        target_value = ith_bit(self.state["d"][5], i)
        new_condition = conditional_value("c", 5, i, target_value)
        self.update_for_conditional_value(new_condition)
        print "New c value:     "+bin(2**33 + self.state["c"][5])[2:]

        # add additional 1st round conditions
        c1 = conditional_value("d", 2, i-9, 0)
        c2 = conditional_equality("a", 2, i-9, "b", 1, i-9)
        c3 = conditional_value("c", 2, i-9, 0)
        c4 = conditional_value("b", 2, i-9, 0)
        self.update_for_r1_conditions([c1, c2, c3, c4])

        self.msg = self.derive_m_from_state()
        words = self.m_to_words(self.msg)

        words[5] = (words[5] + 2**(i-17)) & 0xffffffff
        words[8] = (words[8] - 2**(i-10)) & 0xffffffff
        words[9] = (words[9] - 2**(i-10)) & 0xffffffff

        self.msg = self.words_to_m(words)
        self.state = md4_states(self.msg)
        print "New target value is " + str(ith_bit(self.state["d"][5], i))
        print "NewNew c value:  "+bin(2**33 + self.state["c"][5])[2:]

    def derive_m_from_state(self):
        # Derives m from the first round state variables.
        a = self.state["a"]
        b = self.state["b"]
        c = self.state["c"]
        d = self.state["d"]

        m = []

        m0  = f1_inv(a[1], 3, a[0], b[0], c[0], d[0])
        m1  = f1_inv(d[1], 7, d[0], a[1], b[0], c[0])
        m2  = f1_inv(c[1],11, c[0], d[1], a[1], b[0])
        m3  = f1_inv(b[1],19, b[0], c[1], d[1], a[1])

        m += [m0, m1, m2, m3]

        m4  = f1_inv(a[2], 3, a[1], b[1], c[1], d[1])
        m5  = f1_inv(d[2], 7, d[1], a[2], b[1], c[1])
        m6  = f1_inv(c[2],11, c[1], d[2], a[2], b[1])
        m7  = f1_inv(b[2],19, b[1], c[2], d[2], a[2])

        m += [m4, m5, m6, m7]

        m8  = f1_inv(a[3], 3, a[2], b[2], c[2], d[2])
        m9  = f1_inv(d[3], 7, d[2], a[3], b[2], c[2])
        m10 = f1_inv(c[3],11, c[2], d[3], a[3], b[2])
        m11 = f1_inv(b[3],19, b[2], c[3], d[3], a[3])

        m += [m8, m9, m10, m11]

        m12 = f1_inv(a[4], 3, a[3], b[3], c[3], d[3])
        m13 = f1_inv(d[4], 7, d[3], a[4], b[3], c[3])
        m14 = f1_inv(c[4],11, c[3], d[4], a[4], b[3])
        m15 = f1_inv(b[4],19, b[3], c[4], d[4], a[4])

        m += [m12, m13, m14, m15]
        self.msg = self.words_to_m(m)

        return self.msg
