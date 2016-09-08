import gensafeprime
import sys
from os import urandom

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
        return m

    def valid_padding(self, m_int):
        hex_string = ("0x%0*x"%(self.bits/4, m_int))[2:]
        return hex_string[:2] == "00" and hex_string[2:4] == "02"


def oracle_decrypt(P, c, e, n):
    upper = n
    lower = 0
    exp = 1
    while upper-lower > 1:
        interval_width = upper - lower
        next_delta = interval_width//2
        c = (modExp(2, e, n) * c) % n
        if P.check_parity(c):
            upper -= next_delta
        else:
            lower += next_delta
        exp+=1
        print int_to_message(upper).decode('hex')

def padding_oracle_decrypt(oracle, c, e, n):
    num_bits = oracle.bits
    k = num_bits / 8
    B = 2**(8*(k-2))
    lower = 2*B
    upper = 3*B - 1
    s = get_first_s(oracle, c, e, n, B)
    print s
    while True:
        s, lower, upper = get_next_s(oracle, s, B, c, e, n, lower, upper)
        print s, lower, upper, upper - lower

def get_first_s(oracle, c, e, n, B):
    s = n//(3*B) + 1
    c = (c * modExp(s, e, n)) % n
    i = 0
    while not oracle.check_padding(c):
        i+=1
        s += 1
        c = (c * modExp(s, e, n)) % n
    return s

def get_next_s(oracle, s_old, B, c, e, n, lower_bound, upper_bound):
    i = 1
    while True:
        r_lb_num = upper_bound*s_old - 2*B
        r_lb = 2*r_lb_num / n
        r = r_lb + i

        s_lb = (2*B + r*n)/upper_bound
        s_ub = (3*B + r*n)/lower_bound
        delta = s_ub - s_lb - 1
        j = 1
        while j < delta:
            s = s_lb + j
            c = (c * modExp(s, e, n)) % n
            if oracle.check_padding(c):
                r_lb = (lower_bound * s - 3 * B + 1) / n + 1
                r_ub = (upper_bound * s - 2 * B) / n
                a = max(lower_bound, (2*B + r_lb*n)/s)
                b = min(upper_bound, (3*B - 1 + r_ub*n)/s)
                return s, a, b
            j += 1
        i += 1




def main():
    sys.setrecursionlimit(4000)
    print "Generating keys ..."
    P = RSA_padding_oracle(128)
    e, n = P.get_public_keys()
    m = "Kick it!!!"
    mp = P.pad_plaintext(m)
    c = rsa_encrypt(mp, e, n)
    padding_oracle_decrypt(P, c, e, n)

if __name__ == "__main__":
    main()
