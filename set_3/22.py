import mersenne_twister
import random
import time

def get_first_rn():
    seed = random.randint(1000,500000)
    rng = mersenne_twister.mersenne_rng(seed = seed)
    return seed, rng.get_random_number()

def int_32(num):
    return int(0xFFFFFFFF & num)

def back_out_right_shift(num,shift_number):
    # get most significant bits
    lower_mask = (1<<(32-shift_number))-1
    upper_mask = ((1<<32)-1)-lower_mask
    most_sig_bits = num & upper_mask

    # get least significant bits
    lower_mask_2 = (1<<(shift_number))-1
    upper_mask_2 = ((1<<32)-1)-lower_mask_2
    right_part = num & lower_mask
    left_part = (num & upper_mask_2) >> shift_number
    least_sig_bits = right_part ^ left_part

    # return the concatenation of both (the sum in this case)
    return most_sig_bits + least_sig_bits

def back_out_left_shift_and(num, shift_number, and_number):
    # get least significant bits
    lower_mask_1 = (1<<shift_number)-1
    least_sig_bits = num & lower_mask_1

    # get middle blocks
    num_middle_blocks = 32//shift_number-1
    middle_blocks = []
    previous_block = least_sig_bits
    for i in range(num_middle_blocks):
        lower_mask = (1<<(shift_number*(i+2)))-1
        lower_mask_2 = (1<<(shift_number*(i+1)))-1
        upper_mask = ((1<<32)-1)-lower_mask_2
        input_bits = (num & upper_mask) & lower_mask
        output_bits = input_bits^((previous_block<<shift_number)&and_number)
        middle_blocks.append(output_bits)
        previous_block = output_bits

    # get final block
    final_block_length = 32%shift_number
    lower_mask = (1<<(32-final_block_length))-1
    upper_mask = ((1<<32)-1) - lower_mask
    input_bits = num & upper_mask
    shifted_output = int_32(middle_blocks[-1]<<shift_number)
    final_block = input_bits ^ (shifted_output & and_number)

    # sum elements
    c = final_block + least_sig_bits
    for block in middle_blocks:
        c+=block

    return c

def get_state_0(y):
    y = back_out_right_shift(y,18)
    y = back_out_left_shift_and(y,15,0xEFC60000)
    y = back_out_left_shift_and(y,7,0x9D2C5680)
    y = back_out_right_shift(y,11)
    return y


def crack_seed(first_randint):
    s0 = get_state_0(first_randint)
    return s0

def test_first_shift():
    for i in range(100):
        x = random.randint(100,1000000)
        y = x^(x>>11)
        assert back_out_right_shift(y,11)==x
    print 'test complete'

def test_second_shift():
    for i in range(100):
        x = random.randint(100,1000000)
        y = x^((x<<7)&0x9D2C5680)
        assert back_out_left_shift_and(y,7,0x9D2C5680)==x
    print 'test complete'



if __name__ == "__main__":
    seed, rn = get_first_rn()
    for i in range(1000,500000):
        m = mersenne_twister.mersenne_rng(seed = i)
        if rn == m.get_random_number():
            print "Seed guess: "+str(i)
            print "Actual seed: "+str(seed)
            break
