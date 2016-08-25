import random, hashlib, sys
sys.setrecursionlimit(3000)
p, g = 37, 5
a = random.randint(0, 37)
A = (g**a)%37
b = random.randint(0, 37)
B = (g**b)%37
s = (B**a)%p
t = (A**b)%p
#print(s, t)
p = 'ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff'
p = int(p, 16)
#print(p)
m = hashlib.sha256()
m.update(str(s).encode('utf-8'))
#print(m.digest())
n = hashlib.sha256()
n.update(str(s).encode('utf-8'))
#print(2**random.randint(1, p))
def modExp(base, exp, p):
	if exp == 1: return base%p
	if exp%2 == 0: return (modExp(base, exp//2, p)**2)%p
	else: return (modExp(base, 1, p)*modExp(base, exp - 1, p))%p
#print(modExp(5, 117, 19))
g = 2
a = random.randint(1, p)
A = modExp(g, a, p)
b = random.randint(1, p)
B = modExp(g, b, p)
s = modExp(B, a, p)
t = modExp(A, b, p)
print(s == t)
