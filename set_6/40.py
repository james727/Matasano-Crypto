import gensafeprime
import math
import random

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
        return hex(i)[2:].decode('hex')
    return hex(i)[2:-1].decode('hex')

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

    return guess if n_power(guess) == k else upper

class decryption_oracle(object):
    def __init__(self):
        self.p = gensafeprime.generate(300) #300 bit primes
        self.q = gensafeprime.generate(300)
        self.n = self.p*self.q
        self.e, self.d = generate_key_pair(self.p, self.q)
        self.texts = ["I like cheese",
                      "I like cryptography",
                      "I'm not very good at this",
                      "hmmmmmmmm",
                      "Do your worst!",
                      "I bet you can't decrypt this"]

    def get_public_keys(self):
        return self.e, self.n

    def get_ciphertext(self):
        return rsa_encrypt(random.choice(self.texts), self.e, self.n)

    def decrypt_ciphertext(self, c):
        return modExp(c, self.d, self.n)

def main():
    oracle = decryption_oracle()
    e, n = oracle.get_public_keys()
    c = oracle.get_ciphertext()
    s = random.randint(1,n**(1.0/10))
    cp = (modExp(s, e, n) * c) % n
    pp = oracle.decrypt_ciphertext(cp)
    i = invmod(s,n)
    print int_to_message((pp*i)%n)


if __name__ == "__main__":
    main()
