import gensafeprime
import math
import random
import sha1
import sys
import os

def sha1_hexdigest(txt):
    sha = sha1.SHA1()
    sha.update(txt)
    return sha.hexdigest()

def invmod(e, n):
    # get the multiplicative inverse of e modulo n
    _, d, _ = extended_euler(e,n)
    return d%n

def extended_euler(a, b):
    r_old, s_old, t_old = a, 1, 0
    r_current, s_current, t_current = b, 0, 1
    r_new = 1

    while r_new != 0:
        q = r_old // r_current
        r_new = r_old - q * r_current
        s_new = s_old - q * s_current
        t_new = t_old - q * t_current

        r_old, s_old, t_old = r_current, s_current, t_current
        r_current, s_current, t_current = r_new, s_new, t_new

    return r_old, s_old, t_old

def generate_key_pair(p, q):
    # generate a public and private key for a given pair of primes
    n = p*q
    totient = (p-1)*(q-1)
    e = 3
    d = invmod(e, totient)
    return e, d

def modExp(base, exp, p):
	if exp == 1: return base%p
	if exp%2 == 0: return (modExp(base, exp//2, p)**2)%p
	else: return (modExp(base, 1, p)*modExp(base, exp - 1, p))%p

def rsa_encrypt(m, e, n):
    i = message_to_int(m)
    c = modExp(i, e, n)
    return c

def rsa_decrypt(c, d, n):
    m = modExp(c, d, n)
    return int_to_message(m)

def message_to_int(m):
    return int(m.encode('hex'), 16)

def int_to_message(i):
    hexmsg = hex(i)[2:]
    if hexmsg[-1] != 'L':
        hexmsg = hex(i)[2:]
    else:
        hexmsg = hex(i)[2:-1]
    hexmsg = "0"*3 + hexmsg #re-padding because of hex decoding problems.. leading zeroes get erased
    return hexmsg.decode('hex')

def n_root(k, n):
    # solve for the nth root of k using binary search...
    def n_power(k):
        return k**n

    lower = 0
    upper = k
    guess = (lower+upper)/2
    e = n_power(guess)

    while e != k and upper - lower > 1:
        if e > k:
            upper = guess
        else:
            lower = guess
        guess = (lower+upper)/2
        e = n_power(guess)

    return guess if n_power(guess) == k else lower

class rsa_sig_validator(object):
    def __init__(self):
        self.p = gensafeprime.generate(512) #512 bit primes for speed/recursion depth
        self.q = gensafeprime.generate(512)
        self.n = self.p*self.q
        self.e, self.d = generate_key_pair(self.p, self.q)
        self.plaintext = "hi mom"

    def get_public_keys(self):
        return self.d, self.n

    def validate_ciphertext(self, c):
        plaintext = rsa_decrypt(c, self.e, self.n)
        message = self.remove_padding(plaintext)
        return message == sha1_hexdigest(self.plaintext)

    def remove_padding(self, m):
        m = m[2:]
        index = m.index(chr(0))
        hash_length = 40
        return m[index+1:index+40+1]

def pad_plaintext(txt_hash):
    num_bits = 1024
    num_bytes = num_bits/8
    prefix = chr(0) + chr(1)
    postfix = chr(0)
    message_len = len(prefix) + len(postfix) + len(txt_hash)
    padding_needed = num_bytes - message_len
    padding = chr(255)*padding_needed
    return prefix + padding + postfix + txt_hash

def get_forged_ciphertext(text):
    h = sha1_hexdigest(text)
    garbage_length = 85 #need enough garbage that the cube root approximation leaves the message intact
    padded_txt = pad_plaintext(h+os.urandom(garbage_length))
    cube_root = n_root(message_to_int(padded_txt), 3)
    return cube_root


def main():
    sys.setrecursionlimit(2000)
    R = rsa_sig_validator()
    d, n = R.get_public_keys()
    txt = "hi mom"
    forged_text = get_forged_ciphertext(txt)
    print R.validate_ciphertext(forged_text)

if __name__ == "__main__":
    main()
