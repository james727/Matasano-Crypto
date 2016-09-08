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
    if base == 0:
        return 0
    elif exp == 1:
        return base%p
    elif exp%2 == 0:
        return (modExp(base, exp//2, p)**2)%p
    else:
        return (modExp(base, 1, p)*modExp(base, exp - 1, p))%p

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

def generate_DSA_params(g = False):
    p = "800000000000000089e1855218a0e7dac38136ffafa72eda7\
     859f2171e25e65eac698c1702578b07dc2a1076da241c76c6\
     2d374d8389ea5aeffd3226a0530cc565f3bf6b50929139ebe\
     ac04f48c3c84afb796d61e5a4f9a8fda812ab59494232c7d2\
     b4deb50aa18ee9e132bfa85ac4374d7f9091abc3d015efc87\
     1a584471bb1"
    q = "f4f47f05794b256174bba6e9b396a7707e563c5b"
    if not g:
        g = "5958c9d3898b224b12672c0b98e06c60df923cb8bc999d119\
         458fef538b8fa4046c8db53039db620c094c9fa077ef389b5\
         322a559946a71903f990f1f7e0e025e2d7f7cf494aff1a047\
         0f5b64c36b625a097f1651fe775323556fe00b3608c887892\
         878480e99041be601a62166ca6894bdd41a7054ec89f756ba\
         9fc95302291"
        g = int(''.join(g.split()), 16)
    return int(''.join(p.split()), 16), int(''.join(q.split()), 16), g

def get_pk_from_k(k, s, h, r, q):
    temp1 = (s*k)%q
    temp2 = (temp1 - h)%q
    return (invmod(r, q)*temp2)%q

def get_k_from_mult_msgs(h1, h2, s1, s2, q):
    temp1 = (h1-h2)%q
    temp2 = (s1-s2)%q
    denom = invmod(temp2, q)
    return (temp1*denom)%q

class DSA_signer(object):
    def __init__(self, g = False):
        self.p, self.q, self.g = generate_DSA_params(g)
        self.x = random.randint(1, self.q)
        self.y = modExp(self.g, self.x, self.p)

    def DSA_sign(self, h):
        k = random.randint(1, self.q)
        r = modExp(self.g,k,self.p)%self.q
        temp = (h%self.q + (self.x*r)%self.q)%self.q
        s = (invmod(k, self.q) * temp)%self.q
        return r, s

class DSA_verifier(object):
    def __init__(self, g = False):
        self.p, self.q, self.g = generate_DSA_params(g)

    def verify(self, S, r, s, h):
        w = invmod(s, self.q)
        u1 = (h * w) % self.q
        u2 = (r * w) % self.q
        v = ((modExp(self.g, u1, self.p) * modExp(S.y, u2, self.p)) % self.p) % self.q
        return v == r

def forge_r_s(y, z, p, q):
    r = modExp(y, z, p) % q
    s = (invmod(z, q) * r) % q
    return r, s

def test_g_zero():
    # recursion limit :(
    sys.setrecursionlimit(2000)

    # generate signature
    m = "hello, world"
    h = int(sha1_hexdigest(m), 16)
    S = DSA_signer(g = 0)
    r, s = S.DSA_sign(h)

    # verify signature
    V = DSA_verifier(g = 0)
    print V.verify(S, r, s, h)

    forged_signature = "omgwtfbbq"
    h = int(sha1_hexdigest(forged_signature), 16)
    print V.verify(S, r, s, h)

def test_g_p_plus():
    # generate signature
    m = "hello, world"
    h = int(sha1_hexdigest(m), 16)
    S = DSA_signer()
    r, s = S.DSA_sign(h)

    # forge signature
    V = DSA_verifier(g = 1)
    z = random.randint(1, S.q)
    r, s = forge_r_s(S.y, z, S.p, S.q)

    # set up new message hash
    m = "Hello, world"
    h = int(sha1_hexdigest(m), 16)
    print V.verify(S, r, s, h)

    m = "Goodbye, world"
    h = int(sha1_hexdigest(m), 16)
    print V.verify(S, r, s, h)

if __name__ == "__main__":
    #test_g_zero()
    test_g_p_plus()
