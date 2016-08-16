from mersenne_twister import mersenne_rng
import os


def int_32(num):
    return int(0xFFFFFFFF & num)

def back_out_right_shift(num,shift_number):
    # get most significant bits
    lower_mask = (1<<(32-shift_number))-1
    upper_mask = ((1<<32)-1)-lower_mask
    most_sig_bits = num & upper_mask
    #print "Number in binary: "+bin(num)
    #print "Upper mask:       "+bin(upper_mask)
    #print "Most sig bits:    "+bin(most_sig_bits)+"\n"

    num_other_blocks = 32//shift_number-1
    middle_blocks = []
    previous_block = most_sig_bits
    for i in range(num_other_blocks):
        lower_mask = (1<<(32-shift_number*(i+1)))-1
        lower_mask_2 = (1<<(32-shift_number*(i+2)))-1
        upper_mask = ((1<<32)-1)-lower_mask_2
        input_bits = (num & upper_mask) & lower_mask
        output_bits = input_bits^(previous_block>>shift_number)
        middle_blocks.append(output_bits)
        previous_block = output_bits
        #print "Middle lower mask:  "+bin(lower_mask)
        #print "Middle upper mask:  "+bin(upper_mask)
        #print "Middle masked bits: "+bin(input_bits)

    # get final block
    final_block_length = 32%shift_number
    lower_mask = (1<<final_block_length)-1
    input_bits = num & lower_mask
    shifted_output = int_32(middle_blocks[-1]>>shift_number) if len(middle_blocks)>0 else int_32(most_sig_bits>>shift_number)&lower_mask
    final_block = input_bits ^ (shifted_output)

    """# get least significant bits
    lower_mask_2 = (1<<(shift_number))-1
    upper_mask_2 = ((1<<32)-1)-lower_mask_2
    right_part = num & lower_mask
    left_part = (num & upper_mask_2) >> shift_number
    least_sig_bits = right_part ^ left_part

    print [chr(x) for x in ]

    # return the concatenation of both (the sum in this case)
    return most_sig_bits + least_sig_bits"""

    # sum elements
    c = most_sig_bits+final_block
    for block in middle_blocks:
        c+=block
    return c

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

def get_rng():
    seed = 438276439281463287
    return mersenne_rng(seed = int(seed))

def get_next_624(rng):
    return [rng.get_random_number() for _ in range(624)]

def get_original_state(consecutive_rns):
    return [get_state_0(x) for x in consecutive_rns]

def create_new_rng(original_state):
    new_rng = mersenne_rng()
    new_rng.state = original_state
    new_rng.index = 624
    return new_rng

def main():
    rng = get_rng()
    rn_seq = get_next_624(rng)
    original_state = get_original_state(rn_seq)
    cloned_rng = create_new_rng(original_state)
    for i in range(100):
        n1 = rng.get_random_number()
        n2 = cloned_rng.get_random_number()
        print "%10d %10d %5s"%(n1,n2,n1==n2)

def transform_and_print(y):
    u = 11
    s = 7
    b = 0x9D2C5680
    t = 15
    c = 0xEFC60000
    l = 18
    print "\nStarting y value: "+str(y)
    y = y^(y>>u)
    print "After first transformation: "+str(y)
    y = y^((y<<s)&b)
    print "After second transformation: "+str(y)
    y = y^((y<<t)&c)
    print "After third transformation: "+str(y)
    y = y^(y>>l)
    print "After fourth transformation: "+str(y)+"\n"

def back_out_and_print(y):
    print "\nStarting y value: "+str(y)
    y = back_out_right_shift(y,18)
    print "After first transformation: "+str(y)
    y = back_out_left_shift_and(y,15,0xEFC60000)
    print "After second transformation: "+str(y)
    y = back_out_left_shift_and(y,7,0x9D2C5680)
    print "After third transformation: "+str(y)
    y = back_out_right_shift(y,11)
    print "After fourth transformation: "+str(y)+"\n"


def test():
    rng = get_rng()
    num = rng.get_random_number()
    state_0 = get_state_0(num)
    real_s0 = rng.state[0]
    transform_and_print(real_s0)
    back_out_and_print(num)

if __name__ == "__main__":
    main()
