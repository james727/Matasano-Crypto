from os import urandom
from Crypto.Cipher import AES
import itertools
import math
import random

BLOCK_SIZE = 16
INITIAL_VALUE = "YELLOW SUBMARINE"
COUNTER = 0

# Solution to cryptopals 53. Algorithms roughly based on the pseudocode in
# Kelsey and Schneier's original expandable message paper. WARNING: There
# are errors in the original pseudocode; don't take it as gospel.

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
    h = pks_padding(h, BLOCK_SIZE)
    return ecb_encrypt(m_block, h)[:4]


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

def gen_collision_pair():
    hashes = {}
    while True:
        m = urandom(16)
        h = my_better_hash(m)
        if h in hashes:
            return m, hashes[h]
        hashes[h] = m

def find_collision(l, h_in):
    # process dummy blocks
    h_tmp = h_in
    q = '0'*BLOCK_SIZE
    for i in range(l-1):
        h_tmp = my_better_c(q, h_tmp)

    A = {}
    for i in range(2**16):
        m = urandom(BLOCK_SIZE)
        A[my_better_c(m, h_in)] = m

    collision_found = False
    while not collision_found:
        m = urandom(BLOCK_SIZE)
        new_h = my_better_c(m, h_tmp)
        if new_h in A:
            short_message = A[new_h]
            long_message = q * (l-1) + m
            h_int = new_h
            return short_message, long_message, h_int

def test_find_collision():
    h0 = "MBH1"
    s, l, h = find_collision(8, h0)
    assert len(l) == 8 * BLOCK_SIZE
    assert len(s) == BLOCK_SIZE
    assert my_better_hash(s) == my_better_hash(l)
    print "generating all msgs"
    expandable_messages(8, h0)

def expandable_messages(k, h_in):
    h_tmp = h_in
    C = []
    for i in range(k):
        h_old = h_tmp
        m0, m1, h_tmp = find_collision(2**i + 1, h_tmp)
        assert my_better_hash_test(m0, h_old) == h_tmp
        assert my_better_hash_test(m1, h_old) == h_tmp
        C = [[m0, m1, h_tmp]] + C
    return C, h_tmp

def gen_intermediate_states(m):
    num_blocks = len(m) / 16
    h_int = "MBH1"
    D = {}
    for i in range(num_blocks):
        D[h_int] = i
        current_block = m[BLOCK_SIZE*i:BLOCK_SIZE*(i+1)]
        h_int = my_better_c(current_block, h_int)
    D[h_int] = num_blocks
    return D

def find_intermediate_collision(intermediate_states, h_int, k):
    while True:
        test_block = urandom(BLOCK_SIZE)
        new_h = my_better_c(test_block, h_int)
        if new_h in intermediate_states and intermediate_states[new_h] > k:
            return test_block, intermediate_states[new_h]

def test_intermediate_states():
    m = urandom(BLOCK_SIZE*2**6)
    gen_intermediate_states(m)

def gen_expandable_message(messages, length, k):
    print "Generating expandable message of length {}".format(length)
    M = ""
    T = length - k
    i = 0
    for i in range(k):
        if T >= 2**(k-1-i):
            M = messages[i][1] + M
            print "Iteration {}: T = {}, longer block = {}, selecting longer message of length: {} blocks".format(i, T, 2**(k-1-i), len(messages[i][1])//16)
            T -= 2**(k-1-i)
        else:
            M = messages[i][0] + M
            print "Iteration {}: T = {}, longer block = {}, selecting shorter message of length: {} blocks".format(i, T, 2**(k-1-i), len(messages[i][0])//16)
    return M

def test_exp_msgs():
    k = 8
    m = urandom(BLOCK_SIZE*2**k)
    exp_messages, h_int = expandable_messages(k, "MBH1")
    for i in range(10):
        new = ""
        for m in reversed(exp_messages):
            msgs = m[:2]
            new += random.choice(msgs)
        assert my_better_hash(new) == h_int

def test_message_generation():
    k = 8
    m = urandom(BLOCK_SIZE*2**k)
    exp_messages, h_int = expandable_messages(k, "MBH1")
    for i in range(k, 2**(k-2)):
        m = gen_expandable_message(exp_messages, i, k)
        assert my_better_hash(m) == h_int
        print len(m)/16, i
        #assert len(m)/16 == i

def expandable_message_attack(k):
    # generates a random string of length 2**k and finds a same-length collision_blocks
    # using the expandable message attack. This uses my 32 bit hash function my_better_hash
    m = urandom(BLOCK_SIZE*2**k) # done
    h_target = my_better_hash(m) # done
    print "Generating expandable messages..."
    exp_messages, h_int = expandable_messages(k, "MBH1") # done
    print "Got messages"
    print "Getting intermediate states...."
    intermediate_states = gen_intermediate_states(m) # intermediate_states for i = k, ...2**k-1
    print "Got states"
    print "Getting a collision..."
    block, bridge_index = find_intermediate_collision(intermediate_states, h_int, k)
    print "Got collision"
    print "Generating expandable message"
    exp_message = gen_expandable_message(exp_messages, bridge_index-1, k)
    print "Done"
    new_m = exp_message + block + m[16*bridge_index:]
    assert my_better_hash(new_m) == my_better_hash(m)
    assert len(new_m) == len(m)
    # If the above assertions pass we've successfully created a collision message
    # of the same length as the original


def tests():
    text_exp_msgs()
    test_message_generation()

if __name__ == "__main__":
    expandable_message_attack(8)
