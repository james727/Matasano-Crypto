from os import urandom
from Crypto.Cipher import AES
import itertools


BLOCK_SIZE = 16
INITIAL_VALUE = "YELLOW SUBMARINE"
COUNTER = 0

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

def my_c(m_block, h):
    return ecb_encrypt(m_block, h)[:2]

def my_better_c(m_block, h):
    return ecb_encrypt(m_block, h)[:4]

def my_hash(text, h0):
    text = pks_padding(text, BLOCK_SIZE)
    H = h0
    for i in range(len(text)/16):
        block = text[16*i:16*(i+1)]
        H = my_c(block, pks_padding(H, BLOCK_SIZE))
    return H

def my_better_hash(text):
    text = pks_padding(text, BLOCK_SIZE)
    H = "MBH1"
    for i in range(len(text)/16):
        block = text[16*i:16*(i+1)]
        H = my_better_c(block, pks_padding(H, BLOCK_SIZE))
    return H

def gen_collision_pair(h0):
    global COUNTER
    COUNTER += 1
    hashes = {}
    while True:
        m = urandom(16)
        h = my_hash(m, h0)
        if h in hashes:
            return m, hashes[h]
        hashes[h] = m

def gen_better_collision_pair():
    hashes = {}
    while True:
        m = urandom(16)
        h = my_better_hash(m)
        if h in hashes:
            return m, hashes[h]
        hashes[h] = m

def gen_2n_collisions(n, h0):
    blocks = []
    index = 1
    while index <= n:
        m1, m2 = gen_collision_pair(h0)
        h0 = my_hash(m1, h0)
        blocks.append((m1, m2))
        index+=1
    return blocks

def gen_combinations(collision_blocks):
    if len(collision_blocks) == 1:
        return list(collision_blocks[0])
    else:
        b1, b2 = collision_blocks[0]
        out = []
        collision_blocks = collision_blocks[1:]
        for combo in gen_combinations(collision_blocks):
            out.append(b1 + combo)
            out.append(b2 + combo)
        return out

def test():
    h0 = "29"
    p1, p2 = gen_collision_pair(h0)
    assert my_hash(p1, h0) == my_hash(p2, h0) and p1 != p2

def test_collisions(blocks, h0):
    for m1 in blocks:
        for m2 in blocks:
            assert my_hash(m1, h0) == my_hash(m2, h0)

def part_1():
    h0 = "42"
    blocks = gen_2n_collisions(4, h0)
    combos = gen_combinations(blocks)
    test_collisions(combos, h0)

def find_better_hash_collisions(collns):
    d = {}
    for c in collns:
        h = my_better_hash(c)
        if h in d:
            return c, d[h]
        else:
            d[h] = c
    return False

def part_2():
    b1 = 16
    b2 = 32
    h0 = "bl"

    found = False
    collisions = set()
    while not found:
        collns = gen_2n_collisions(b2/2, h0)
        combos = set(gen_combinations(collns))
        collisions = collisions | combos
        x = find_better_hash_collisions(combos)
        if x:
            print "found collisions for f + g in {} calls to the collison function".format(COUNTER)
            found = True

    assert my_hash(x[0], h0) + my_better_hash(x[0]) == my_hash(x[1], h0) + my_better_hash(x[1]) 

if __name__ == "__main__":
    part_1()
    part_2()
