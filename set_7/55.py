import md4, wangs_conditions
from wangs import *
from os import urandom, system, name
import random
from struct import pack, unpack

# Hello reader! When I ran this it took approximately 3 minutes to generate
# a collision, and generated the following messages (hex encoded):
#
# m1 = 15a21fd5d7a4abacc3bf69d747f9b1817473b272d9f83dc8c9295179f595a5b733e4f82b6a2664f3092e5c340b2cc4682bc5615fc2b756634b44cce91fbe36b8
# m2 = 15a21fd5d7a4ab2cc3bf694747f9b1817473b272d9f83dc8c9295179f595a5b733e4f82b6a2664f3092e5c340b2cc4682bc5605fc2b756634b44cce91fbe36b8
#
# To verify this, please feel free to run the method "test_final_collisions"

BLOCK_SIZE = 64

def first_round_modifications(m):
    # Imposes the set of first round conditions
    # listed in table 6 of Wang's paper necessary
    # to get to 2^-25 probability of collision
    state0 = md4_state(m)
    conditions = wangs_conditions.first_round_conditions()
    state0.update_for_r1_conditions(conditions)
    return state0.state, state0.derive_m_from_state()

def second_round_modifications(m):
    # Imposes the set of second round conditions
    # necessary to get to 2^-25 probability of collision
    state0 = md4_state(m)
    conditions = wangs_conditions.second_round_conditions()
    state0.update_for_r2_conditions(conditions)
    return state0.state, state0.msg
    return state0.state, state0.derive_m_from_state()

def modify_m(m):
    # Takes an m and imposes some conditions
    # that make a collision likely
    s, m = first_round_modifications(m)
    s, m = second_round_modifications(m)
    return m

def set_key_bits(m):
    nums = [unpack("<I", m[4*i:4*(i+1)])[0] for i in range(16)]
    nums[1] = update_for_equality(nums[1], 32, 0)
    nums[2] = update_for_equality(nums[2], 32, 0)
    nums[2] = update_for_equality(nums[2], 29, 1)
    nums[12] = update_for_equality(nums[12], 17, 1)
    m = ""
    for num in nums:
        m += pack("<I", num)
    return m

def tweak_bits_2(m):
    nums = [unpack("<I", m[4*i:4*(i+1)])[0] for i in range(16)]
    nums[1] += 2**31
    nums[2] += 2**31-2**28
    nums[12] -= 2**16
    m = ""
    for num in nums:
        m += pack("<I", num)
    return m

def tweak_bits(m):
    nums = [unpack("<I", m[4*i:4*(i+1)])[0] for i in range(16)]
    nums[1] = nums[1]^(1<<30)
    nums[2] = nums[2]^(1<<30)^(1<<27)
    nums[12] = nums[12]^(1<<15)
    m = ""
    for num in nums:
        m += pack("<I", num)
    return m

def tweak_bits_3(m):
    nums = [unpack("<I", m[4*i:4*(i+1)])[0] for i in range(16)]
    nums[1] = (nums[1] + 2**31)&0xffffffff
    nums[2] = (nums[2] + 2**31 - 2**28)&0xffffffff
    nums[12] = (nums[12] - 2**16)&0xffffffff
    m = ""
    for num in nums:
        m += pack("<I", num)
    return m

def get_collision():
    i = 0

    conditions1 = wangs_conditions.first_round_conditions()
    conditions2 = wangs_conditions.second_round_conditions()

    while True:
        system('cls' if name == 'nt' else 'clear')
        print "Executing Wang's attack - current iteration is: " + str(i)
        i+=1
        m0 = urandom(BLOCK_SIZE)
        m1 = modify_m(m0)

        m2 = tweak_bits(m1)
        if md4_hash(m1) == md4_hash(m2):
            return m0, m1, m2

        m2 = tweak_bits_3(m1)
        if md4_hash(m1) == md4_hash(m2):
            return m0, m1, m2

def test_ith_bit():
    n = 1<<8
    assert ith_bit(n, 9) == 1
    assert ith_bit(n, 8) == 0
    assert ith_bit(n, 10) == 0
    n = n + 1<<7
    assert ith_bit(n, 8) == 1

def test_update_for_equality():
    n = 0
    n = update_for_equality(n, 8, 1)
    assert ith_bit(n, 8) == 1
    assert ith_bit(n, 7) == 0
    n = update_for_equality(n, 8, 1)
    assert ith_bit(n, 8) == 1
    n = update_for_equality(n, 8, 0)
    assert ith_bit(n, 8) == 0
    n = 3489729842374
    n = update_for_equality(n, 10, 0)
    assert ith_bit(n, 10) == 0
    n = update_for_equality(n, 10, 1)
    assert ith_bit(n, 10) == 1
    c = ith_bit(3489729842374, 10)
    n = update_for_equality(n, 10, c)
    assert n == 3489729842374

def test_first_round_modifications(m):
    state = first_round_modifications(m)[0]
    val1 = state["a"][1]
    val2 = state["b"][0]
    assert ith_bit(val1, 7) == ith_bit(val2, 7)

    val3 = state["b"][2]
    assert ith_bit(val3, 13) == 1
    assert ith_bit(val3, 14) == 1
    assert ith_bit(val3, 20) == 0

    val4 = state["c"][4]
    val5 = state["d"][4]
    assert ith_bit(val4, 19) == ith_bit(val5, 19)
    assert ith_bit(val4, 23) == 1
    assert ith_bit(val4, 26) == 1

def test_rotations():
    for i in range(5):
        n = random.randint(1, 2**31)
        r = random.randint(1, 31)
        assert n == right_rotate(left_rotate(n, r), r)

def test_derive_m_from_state():
    m = urandom(BLOCK_SIZE)
    mp = md4._pad(m)
    md_test = md4_state(m)
    m_der = md_test.derive_m_from_state()[:len(m)]
    assert m_der == m

def test_first_round_integration():
    m0 = urandom(64)
    _, m1 = first_round_modifications(m0)

    conditions = wangs_conditions.first_round_conditions()

    test_message_conditions(m1, conditions)

def test_second_round_integration():
    m0 = urandom(64)
    _, m1 = first_round_modifications(m0)
    _, m2 = second_round_modifications(m1)

    conditions1 = wangs_conditions.first_round_conditions()
    conditions2 = wangs_conditions.second_round_conditions()
    print len(conditions1)
    print len(conditions2)

    test_message_conditions(m2, conditions1)
    test_message_conditions(m2, conditions2)

def test_message_conditions(m, c):
    print "checking if conditions hold ..."
    state = md4_state(m).state
    for i, cond in enumerate(c):
        if not cond.condition_fulfilled(state):
            print cond.state_variable, cond.index, cond.bit
        cond.assert_condition_fulfilled(state)

def test_bit_flipping():
    m0 = urandom(64)
    _, m1 = first_round_modifications(m0)
    _, m2 = second_round_modifications(m1)

    m31 = tweak_bits(m2)
    m32 = tweak_bits_3(m2)

    return

def test():
    test_ith_bit()
    test_update_for_equality()
    m = urandom(BLOCK_SIZE)
    test_first_round_modifications(m)
    test_rotations()
    test_derive_m_from_state()
    test_first_round_integration()
    test_second_round_integration()
    test_bit_flipping()

def test_final_collisions():
    m1 = "15a21fd5d7a4abacc3bf69d747f9b1817473b272d9f83dc8c9295179f595a5b733e4f82b6a2664f3092e5c340b2cc4682bc5615fc2b756634b44cce91fbe36b8".decode('hex')
    m2 = "15a21fd5d7a4ab2cc3bf694747f9b1817473b272d9f83dc8c9295179f595a5b733e4f82b6a2664f3092e5c340b2cc4682bc5605fc2b756634b44cce91fbe36b8".decode('hex')
    assert m1 != m2
    assert md4_hash(m1) == md4_hash(m2)

def main():
    m0, m1, m2 = get_collision()
    print m0.encode('hex')
    print m1.encode('hex')
    print m2.encode('hex')
    assert md4_hash(m1) == md4_hash(m2)
    assert m1 != m2

if __name__ == "__main__":
    main()
