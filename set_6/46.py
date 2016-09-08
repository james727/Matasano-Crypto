import gensafeprime
import sys

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

class parity_oracle(object):
    def __init__(self):
        p = gensafeprime.generate(1024)
        q = gensafeprime.generate(1024)
        self.n = p*q
        self.e, self.d = generate_key_pair(p, q)

    def get_public_keys(self):
        return self.e, self.n

    def check_parity(self, c):
        m = rsa_decrypt_num(c, self.d, self.n)
        return m%2 == 0

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

def main():
    sys.setrecursionlimit(4000)
    print "Generating keys ..."
    P = parity_oracle()
    e, n = P.get_public_keys()
    m = "VGhhdCdzIHdoeSBJIGZvdW5kIHlvdSBkb24ndCBwbGF5IGFyb3VuZCB3aXRoIHRoZSBGdW5reSBDb2xkIE1lZGluYQ==".decode('base64')
    print "Encrypting ..."
    ct = rsa_encrypt(m, e, n)
    oracle_decrypt(P, ct, e, n)

if __name__ == "__main__":
    main()
