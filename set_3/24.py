from mersenne_twister import mersenne_rng
import os
import random

def generate_keystream(text, seed):
    keystream = ''
    rng = mersenne_rng(seed = seed)
    while len(keystream)<len(text):
        rn = rng.get_random_number()
        next_char_bin = bin(rn)[-8:]
        next_char = chr(int(next_char_bin,2))
        keystream+=next_char
    return keystream

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

def random_ciphertext():
    seed = random.randint(0,2**16-1)
    print "The random not-so-secret seed: "+str(seed)
    plaintext = os.urandom(random.randint(1,20))+14*"a"
    ciphertext = mersenne_stream(plaintext, seed)
    return ciphertext


def mersenne_stream(plaintext, seed):
    keystream = generate_keystream(plaintext, seed)
    ciphertext = bitwise_xor(plaintext, keystream)
    return ciphertext

def crack_ciphertext(ct):
    for i in range(2**16-1):
        pt = mersenne_stream(ct, i)
        if pt[-14:] == 14*'a':
            return i, pt
    return 'not found'

def main():
    ct = random_ciphertext()
    print crack_ciphertext(ct)

if __name__ == "__main__":
    main()
