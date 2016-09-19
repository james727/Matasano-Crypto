from os import urandom
from Crypto.Cipher import AES
import itertools
import math
import random

BLOCK_SIZE = 16
INITIAL_VALUE = "YELLOW SUBMARINE"
COUNTER = 0

# Solution to cryptopals 54. Only used my 16 bit hash function for this one.

def pks_padding(plain_text, block_size):
    # modified to not pad final block if multiple of block_size
    final_block_length = len(plain_text)%block_size
    padding_needed = block_size-final_block_length
    if padding_needed == block_size:
        return plain_text
    hex_escape = chr(padding_needed)
    return plain_text+hex_escape*padding_needed

def pks_unpadding(plain_text, block_size):
    last_chr = plain_text[-1]
    if ord(last_chr) < block_size:
        return plain_text[:len(plain_text)-ord(last_chr)]
    else:
        return plain_text

def valid_padding(plain_text, block_size):
    last_chr = plain_text[-1]
    if ord(last_chr) < block_size:
        t_list = list(plain_text)
        c = 0
        while c<ord(last_chr):
            if ord(t_list[-1])!=ord(last_chr):
                raise Exception('Improper PKCS#7 padding')
            t_list.pop(-1)
            c+=1
        return ''.join(t_list)
    else:
        return plain_text

def ecb_encrypt(plain_text, key):
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(plain_text)
    return cipher_text

def my_better_c(m_block, h):
    m_block = pks_padding(m_block, BLOCK_SIZE)
    h = pks_padding(h, BLOCK_SIZE)
    return ecb_encrypt(m_block, h)[:2]


def my_better_hash(text):
    text = pks_padding(text, BLOCK_SIZE)
    H = "MBH1"
    for i in range(len(text)/16):
        block = text[16*i:16*(i+1)]
        H = my_better_c(block, H)
    return H

def my_better_hash_test(text, h_in):
    text = pks_padding(text, BLOCK_SIZE)
    H = h_in
    for i in range(len(text)/16):
        block = text[16*i:16*(i+1)]
        H = my_better_c(block, H)
    return H

def gen_initial_states(k):
    # Generate random set of 2**k hash states
    num_states = 2**k
    states = set()
    while len(states) < num_states:
        states.add(urandom(2))
    return list(states)

def gen_collision(s1, s2):
    # Given two starting states, generates 2 blocks that collide
    h = {}
    for i in range(2**16):
        m1 = urandom(BLOCK_SIZE)
        h1 = my_better_c(m1, s1)
        h[h1] = m1
    while True:
        m2 = urandom(BLOCK_SIZE)
        h2 = my_better_c(m2, s2)
        if h2 in h and m2 != h[h2]:
            return {s1: (h[h2], h2),  s2: (m2, h2)}

def gen_collision_blocks(states):
    # Takes in a list of intermediate hash states and returns a dictionary mapping
    # each state to a message block and next state. Each input state will collide
    # with one other state, so the number of distinct next states will be cut in half.
    # Includes some janky logic to ensure we're generating unique states.
    num_blocks = len(states)
    print "Generating collisions for set of 2**{} states!".format(int(math.log(num_blocks, 2)))
    pairs = [(states[i], states[~i]) for i in range(num_blocks/2)]
    out = {s: None for s in states}
    new_h_list = set()
    for s1, s2 in pairs:
        collns = gen_collision(s1, s2)
        new_h = collns[s1][1]
        while new_h in new_h_list:
            collns = gen_collision(s1, s2)
            new_h = collns[s1][1]
        new_h_list.add(new_h)
        out[s1] = collns[s1]
        out[s2] = collns[s2]
    return out

def gen_diamond_structure(k):
    # Generates the diamond structure as described in Kelsey and Kohno's original paper
    # Structured as a list of dictionaries mapping from intermediate states to blocks and
    # next states
    states = [{x: ("", x) for x in gen_initial_states(k)}]
    current_num_states = 2**k
    while current_num_states > 1:
        current_states = states[-1]
        state_list = list(set([current_states[x][1] for x in current_states]))
        collision_blocks = gen_collision_blocks(state_list)
        states.append(collision_blocks)
        current_num_states/=2
    return states[1:]

def gen_full_message(diamond_structure, s0):
    # Generates a full k-block message based on a diamond structure and starting point
    out = ""
    s_current = s0
    for d in diamond_structure:
        block, s_new = d[s_current]
        out += block
        s_current = s_new
    return s0, out, s_new

def find_collision_block(intermediate_states, h_int):
    intermediate_states = set(intermediate_states)
    print "Finding collision with one of 2**{} states".format(int(math.log(len(intermediate_states),2)))
    while True:
        test_block = urandom(BLOCK_SIZE)
        new_h = my_better_c(test_block, h_int)
        if new_h in intermediate_states:
            return test_block, new_h

def test_gen_collision():
    s1 = urandom(4)
    s2 = urandom(4)
    collns = gen_collision(s1, s2)
    m1 = collns[s1][0]
    m2 = collns[s2][0]
    h2 = collns[s1][1]
    assert my_better_c(m1, s1) == my_better_c(m2, s2)
    assert my_better_c(m1, s1) == h2

def test_gen_initial_states():
    k = 8
    states = gen_initial_states(k)
    s = set()
    for state in states:
        assert state not in s
        assert len(state) == BLOCK_SIZE
        s.add(state)

def test_gen_collision_blocks():
    k = 4
    states = gen_initial_states(k)
    block_dict = gen_collision_blocks(states)
    for b1 in block_dict:
        m1, out_state1 = block_dict[b1]
        for b2 in block_dict:
            m2, out_state2 = block_dict[b2]
            if out_state2 == out_state1:
                assert my_better_c(m1, b1) == my_better_c(m2, b2)
                assert my_better_c(m1, b1) == out_state2

def test_diamond_structure():
    k = 8
    ds = gen_diamond_structure(k)
    for i, s in enumerate(ds):
        next_states = set([s[x][1] for x in s])
        print len(s), len(next_states)
        for state in s:
            block, new_state = s[state]
            assert my_better_c(block, state) == new_state
            if i < len(ds) - 1:
                assert new_state in ds[i+1]

def test_get_full_message():
    k = 4
    d = gen_diamond_structure(k)
    s0 = d[0].keys()[0]
    s0, m, sf = gen_full_message(d, s0)
    assert len(m) == BLOCK_SIZE * k
    assert my_better_hash_test(m, s0) == sf

def tests():
    test_gen_initial_states()
    test_gen_collision()
    test_gen_collision_blocks()
    test_diamond_structure()
    test_get_full_message()

def main():
    P = "I HEREBY PREDICT THE FOLLOWING THINGS: THE PATRIOTS WIN THE WORLD SERIES, THE RED SOX WIN THE SUPER BOWL, AND THE CELTICS WIN THE STANLEY CUP!!!"
    k = 4
    print "Generating diamond structure..."
    diamonds = gen_diamond_structure(k)
    print "Diamonds complete..."
    h_final = diamonds[-1][diamonds[-1].keys()[0]][1]
    final_length = len(P) + BLOCK_SIZE + k * BLOCK_SIZE
    initial_states = diamonds[0].keys()

    int_state = my_better_hash(P)
    print "Finding collision bridge..."
    colln_block, h_colln = find_collision_block(initial_states, int_state)
    print "Found bridge..."

    msg = P + colln_block + gen_full_message(diamonds, h_colln)[1]

    assert len(msg) == final_length
    assert my_better_hash(msg) == h_final
    print "Success!"

if __name__ == "__main__":
    main()
