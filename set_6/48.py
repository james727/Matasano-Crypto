import gensafeprime
import sys
from os import urandom
import math

# Cryptopals set 7 challenge 8
# Note to people who run this script - the first part of the decryption algorithm is SLOW. It will take a few minutes to run.
# Once we get to the logarithmic search, I print out the width of the message interval for your pleasure.


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

def rsa_decrypt_num(c, d, n):
    return modExp(c, d, n)

def message_to_int(m):
    return int(m.encode('hex'), 16)

def int_to_message(i):
    hexmsg = hex(i)[2:-1]
    if len(hexmsg)%2 != 0:
        hexmsg += '0'
    return hexmsg

class RSA_padding_oracle(object):
    def __init__(self, bits):
        p = gensafeprime.generate(bits/2)
        q = gensafeprime.generate(bits/2)
        self.bits = bits
        self.n = p*q
        self.e, self.d = generate_key_pair(p, q)

    def get_public_keys(self):
        return self.e, self.n

    def check_padding(self, c):
        m = rsa_decrypt_num(c, self.d, self.n)
        return self.valid_padding(m)

    def pad_plaintext(self, m):
        # takes in a string, pads it, and converts to int
        num_bytes = self.bits/8
        msg_length = len(m)
        prefix = chr(0) + chr(2)
        postfix = chr(0)
        padding_needed = num_bytes - msg_length - 3
        padding = urandom(padding_needed)
        padded_plaintext = prefix + padding + postfix + m
        return padded_plaintext

    def valid_padding(self, m_int):
        hex_string = ("0x%0*x"%(self.bits/4, m_int))[2:]
        return hex_string[:2] == "00" and hex_string[2:4] == "02"

def padding_oracle_decrypt(oracle, c, e, n):
    num_bits = oracle.bits
    k = num_bits / 8
    B = 2**(8*(k-2))
    lower = 2*B
    upper = 3*B - 1
    M = [(lower, upper)]
    s = get_first_s(oracle, c, e, n, B)
    print "Got first s"
    while True:
        s = get_next_s(oracle, s, B, c, e, n, M)
        M = update_m(B, n, s, M)
        print "Got new M with {} intervals".format(len(M))
        if len(M) == 1:
            a, b = M[0]
            print "Only 1 interval of width " + str(b-a)
            if b - a == 0:
                m = ("0x%0*x"%(num_bits/4, a))[2:]
                return m.decode('hex')

def ceildiv(a, b):
    return -(-a // b)

def update_m(B, n, s, M):
    new_M = []
    for a, b in M:
        rlb = ceildiv(a*s - 3*B + 1, n)
        rub = (b*s - 2*B) // n
        for r in range(rlb, rub + 1):
            new_lb = ceildiv(2*B + r*n, s)
            new_ub = (3*B - 1 + r*n) // s
            new_a = max(a, new_lb)
            new_b = min(b, new_ub)
            if new_b >= new_a:
                new_M.append((new_a, new_b))
    return list(set(new_M))

def merge_intervals(M):
    new_M = []
    M = sorted(M, key = lambda x: x[0])
    for index, interval in enumerate(M):
        a = interval[0]
        b = interval[1]
        if index == 0:
            new_M.append((a,b))
        else:
            old_ub = new_M[-1][1]
            if a <= old_ub and b > old_ub:
                a = new_M[-1][0]
                new_M.pop(-1)
            new_M.append((a,b))
    return new_M

def get_first_s(oracle, c0, e, n, B):
    s = n//(3*B)
    c = (c0 * modExp(s, e, n)) % n
    while not oracle.check_padding(c):
        s += 1
        c = (c0 * modExp(s, e, n)) % n
    return s

def get_next_s_mult_ints(oracle, s_old, c0, e, n):
    s = s_old + 1
    c = (c0 * modExp(s, e, n)) % n
    while not oracle.check_padding(c):
        s += 1
        c = (c0 * modExp(s, e, n)) % n
    return s

def get_next_s_one_int(oracle, s_old, B, c0, e, n, a, b):
    r = 2 * ceildiv(b*s_old - 2*B, n)
    while True:
        s_lb = ceildiv(2*B + r*n, b)
        s_ub = (3*B + r*n) // a
        s = s_lb
        while s <= s_ub:
            cp = (c0 * modExp(s, e, n)) % n
            if oracle.check_padding(cp):
                return s
            s += 1
        r += 1

def get_next_s(oracle, s_old, B, c, e, n, M):
    if len(M) > 1:
        s = get_next_s_mult_ints(oracle, s_old, c, e, n)
    else:
        s = get_next_s_one_int(oracle, s_old, B, c, e, n, M[0][0], M[0][1])
    return s

def main():
    sys.setrecursionlimit(4000)
    print "Generating key pair..."
    P = RSA_padding_oracle(768)
    e, n = P.get_public_keys()
    m = "Kick it!!!"
    mp = P.pad_plaintext(m)
    c = rsa_encrypt(mp, e, n)
    print "Decrypting..."
    print padding_oracle_decrypt(P, c, e, n)

if __name__ == "__main__":
    main()
