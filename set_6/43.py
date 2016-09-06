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

def message_to_int(m):
    return int(m.encode('hex'), 16)

def invmod(e, n):
    # get the multiplicative inverse of e modulo n
    _, d, _ = extended_euler(e,n)
    return d%n

def modExp(base, exp, p):
	if exp == 1: return base%p
	if exp%2 == 0: return (modExp(base, exp//2, p)**2)%p
	else: return (modExp(base, 1, p)*modExp(base, exp - 1, p))%p

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

class DSA_signer(object):
    def __init__(self):
        self.p, self.q, self.g = generate_DSA_params()
        self.x = random.randint(1, self.q)
        self.y = modExp(self.g, self.x, self.p)

    def DSA_sign(self, h):
        k = random.randint(1, self.q)
        r = modExp(self.g,k,self.p)%self.q
        temp = (h%self.q + (self.x*r)%self.q)%self.q
        s = (invmod(k, self.q) * temp)%self.q
        return r, s

class DSA_verifier(object):
    def __init__(self):
        self.p, self.q, self.g = generate_DSA_params()

    def verify(self, S, r, s, h):
        w = invmod(s, self.q)
        u1 = (h * w) % self.q
        u2 = (r*w) % self.q
        v = ((modExp(self.g, u1, self.p) * modExp(S.y, u2, self.p)) % self.p) % self.q
        return v == r

def generate_DSA_params():
    p = "800000000000000089e1855218a0e7dac38136ffafa72eda7\
     859f2171e25e65eac698c1702578b07dc2a1076da241c76c6\
     2d374d8389ea5aeffd3226a0530cc565f3bf6b50929139ebe\
     ac04f48c3c84afb796d61e5a4f9a8fda812ab59494232c7d2\
     b4deb50aa18ee9e132bfa85ac4374d7f9091abc3d015efc87\
     1a584471bb1"
    q = "f4f47f05794b256174bba6e9b396a7707e563c5b"
    g = "5958c9d3898b224b12672c0b98e06c60df923cb8bc999d119\
     458fef538b8fa4046c8db53039db620c094c9fa077ef389b5\
     322a559946a71903f990f1f7e0e025e2d7f7cf494aff1a047\
     0f5b64c36b625a097f1651fe775323556fe00b3608c887892\
     878480e99041be601a62166ca6894bdd41a7054ec89f756ba\
     9fc95302291"
    return int(''.join(p.split()), 16), int(''.join(q.split()), 16), int(''.join(g.split()), 16)

def get_pk_from_k(k, s, h, r, q):
    temp1 = (s*k)%q
    temp2 = (temp1 - h)%q
    return (invmod(r, q)*temp2)%q

def test_signing_verification():
    S = DSA_signer()
    V = DSA_verifier()
    m = "hi whats up"
    h = sha1_hexdigest(m)
    r, s = S.DSA_sign(h)
    print V.verify(S, r, s, h)

def crack_pk():
    p, q, g = generate_DSA_params()
    yt = "84ad4719d044495496a3201c8ff484feb45b962e7302e56a392aee4\
      abab3e4bdebf2955b4736012f21a08084056b19bcd7fee56048e004\
      e44984e2f411788efdc837a0d2e5abb7b555039fd243ac01f0fb2ed\
      1dec568280ce678e931868d23eb095fde9d3779191b8c0299d6e07b\
      bb283e6633451e535c45513b2d33c99ea17"
    y = int("".join(yt.split()),16)
    ht = "d2d0714f014a9784047eaeccf956520045c45265"
    h = int(ht, 16)
    r = 548099063082341131477253921760299949438196259240
    s = 857042759984254168557880549501802188789837994940
    x_target_hash = "0954edd5e0afe5542a4adf012611a91912a3ec16"

    for k in range(2**16):
        x_guess = get_pk_from_k(k, s, h, r, q)
        y_guess = modExp(g, x_guess, p)
        if y_guess == y:
            print "Private key: " + hex(x_guess)[2:-1]
            print sha1_hexdigest(hex(x_guess)[2:-1]) == x_target_hash
            break


if __name__ == "__main__":
    crack_pk()
