import random, hashlib, sys
from Crypto.Cipher import AES
from os import urandom

BLOCK_SIZE = 16
sys.setrecursionlimit(3000)

def modExp(base, exp, p):
	if exp == 1: return base%p
	if exp%2 == 0: return (modExp(base, exp//2, p)**2)%p
	else: return (modExp(base, 1, p)*modExp(base, exp - 1, p))%p

def sha(txt):
    s = hashlib.sha256()
    s.update(txt)
    return s.digest().encode('hex')

def encrypt_aes_cbc(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pks_padding(plain_text, BLOCK_SIZE)
    return cipher.encrypt(padded_text)

def decrypt_aes_cbc(cipher_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text_padded = cipher.decrypt(cipher_text)
    return pks_unpadding(plain_text_padded, BLOCK_SIZE)

def pks_padding(plain_text, block_size):
    final_block_length = len(plain_text)%block_size
    padding_needed = block_size-final_block_length
    hex_escape = chr(padding_needed)
    return plain_text+hex_escape*padding_needed

def pks_unpadding(plain_text, block_size):
    last_chr = plain_text[-1]
    if ord(last_chr) < block_size:
        return plain_text[:len(plain_text)-ord(last_chr)]
    else:
        return plain_text

class server(object):
    def __init__(self, N, g, k, email, password):
        self.N = N
        self.g = g
        self.k = k
        self.email = email
        self.password = password

    def generate_keys(self):
        self.salt = random.randint(1,self.N)
        xH = sha(str(self.salt)+self.password)
        self.password = None
        x = int(xH, 16)
        self.v = modExp(self.g, x, self.N)
        self.b = random.randint(1,self.N)
        self.B = (self.k*self.v + modExp(self.g, self.b, self.N))%self.N

    def send_salt(self, C):
        C.salt = self.salt
        C.B = self.B

    def generate_u(self):
        self.uH = sha(str(self.A)+str(self.B))
        self.u = int(self.uH, 16)

    def process_keys(self):
        tmp1 = self.A*modExp(self.v, self.u, self.N)
        self.S = modExp(tmp1, self.b, self.N)
        self.K = sha(str(self.S))

    def generate_K_digest(self):
        return sha(self.K+str(self.salt))

class client(object):
    def __init__(self, N, g, k, email, password):
        self.N = N
        self.g = g
        self.k = k
        self.email = email
        self.password = password

    def generate_keys(self):
        self.a = random.randint(1,self.N)
        self.A = modExp(self.g,self.a,self.N)

    def send_email(self, S):
        S.A = self.A

    def generate_u(self):
        self.uH = sha(str(self.A)+str(self.B))
        self.u = int(self.uH, 16)

    def process_keys(self):
        xH = sha(str(self.salt)+self.password)
        x = int(xH, 16)
        tmp1 = (self.B - self.k*modExp(self.g,x,self.N))
        tmp2 = self.a+self.u*x
        self.S = modExp(tmp1, tmp2, self.N)
        self.K = sha(str(self.S))

    def generate_K_digest(self):
        return sha(self.K+str(self.salt))

if __name__ == "__main__":
	#initialize constants
    N = int('ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff',16)
    g = 2
    k = 3
    email = "email@email.com"
    password = "password"

	# set up server and client
    S = server(N, g, k, email, password)
    C = client(N, g, k, email, password)

	# generate private and public keys
    S.generate_keys()
    C.generate_keys()

	# client send email, A
    C.send_email(S)
    S.send_salt(C)

	# compute uH, u
    C.generate_u()
    S.generate_u()

    # process keys
    C.process_keys()
    S.process_keys()

    # check key equality
    print S.generate_K_digest()==C.generate_K_digest()
