import random, hashlib, sys
from Crypto.Cipher import AES
from os import urandom
import sha1_2

BLOCK_SIZE = 16
sys.setrecursionlimit(3000)

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

def hmac(key, message):
    h = sha1_2.SHA1()
    if len(key) > 64:
        key = h.update(key).hexdigest()
    elif len(key)<64:
        key = key + '\0'*(64-len(key))

    o_key_pad = bitwise_xor('\\'*64, key)
    i_key_pad = bitwise_xor('6'*64, key)

    h = sha1_2.SHA1()
    h.update(i_key_pad+message)
    tmp_digest = h.hexdigest()
    h = sha1_2.SHA1()
    h.update(o_key_pad + tmp_digest)
    return h.hexdigest()

def modExp(base, exp, p):
	if exp == 1: return base%p
	if exp%2 == 0: return (modExp(base, exp//2, p)**2)%p
	else: return (modExp(base, 1, p)*modExp(base, exp - 1, p))%p

def sha(txt):
    s = hashlib.sha256()
    s.update(txt)
    return s.digest().encode('hex')

def combinations(items, n):
    if n == 0:
        return []
    elif n == 1:
        return [[x] for x in items]
    else:
        prev = combinations(items, n-1)
        out = []
        for c in prev:
            for item in items:
                new = c + [item]
                out.append(new)
        return out

def hmac_sha(txt, key):
    return hmac.hmac(key, txt)

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

class mitm_haxor(object):
    def __init__(self, N, g, k):
        self.N = N
        self.g = g
        self.k = k

    def generate_keys(self):
        self.salt = random.randint(1,self.N)
        self.b = random.randint(1,self.N)
        self.B = modExp(self.g, self.b, self.N)

    def send_salt_u(self, C):
        C.salt = self.salt
        C.B = self.B
        self.u = int(urandom(16).encode('hex'),16)
        C.u = self.u

    def get_password(self):
        hmac_target = self.client_k_digest
        lower_chars = range(65, 91)
        upper_chars = range(97, 123)
        nums = range(48, 58)
        punc = range(33, 48)
        characters = [chr(x) for x in lower_chars+upper_chars+nums+punc]
        current_string = ''
        current_hmac = ''
        pw_length = 1
        while current_hmac != hmac_target:
            potential_passwords = combinations(characters, pw_length)
            for pw in potential_passwords:
                password_guess = ''.join(pw)
                if self.get_hmac(password_guess) == hmac_target:
                    self.password = password_guess
                    return
            pw_length+=1

    def get_hmac(self, password_guess):
        x = int(sha(str(self.salt)+password_guess), 16)
        v = modExp(self.g, x, self.N)
        tmp1 = self.A * modExp(v, self.u, self.N)
        tmp2 = modExp(tmp1, self.b, self.N)
        K = sha(str(tmp2))
        return hmac(K, str(self.salt))

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
        self.email = None
        x = int(xH, 16)
        self.v = modExp(self.g, x, self.N)
        self.b = random.randint(1,self.N)
        self.B = modExp(self.g, self.b, self.N)

    def send_salt_u(self, C):
        C.salt = self.salt
        C.B = self.B
        self.u = int(urandom(16).encode('hex'),16)
        C.u = self.u

    def process_keys(self):
        tmp = self.A*modExp(self.v, self.u, self.N)
        self.S = modExp(tmp, self.b, self.N)
        self.K = sha(str(self.S))

    def generate_K_digest(self):
        return hmac(self.K, str(self.salt))

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
        S.I = self.email
        S.A = self.A

    def process_keys(self):
        xH = sha(str(self.salt)+self.password)
        x = int(xH, 16)
        tmp = self.a+self.u*x
        self.S = modExp(self.B, tmp, self.N)
        self.K = sha(str(self.S))

    def send_K_digest(self, S):
        S.client_k_digest = self.generate_K_digest()

    def generate_K_digest(self):
        return hmac(self.K, str(self.salt))

def main_normal():
    #initialize constants
    N = int('ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff',16)
    g = 2
    k = 3
    email = "email@email.com"
    password = "ab"

	# set up server and client
    M = mitm_haxor(N, g, k)
    C = client(N, g, k, email, password)

	# generate private and public keys
    M.generate_keys()
    C.generate_keys()

	# client send email, A
    C.send_email(M)
    M.send_salt_u(C)

    # process keys
    C.process_keys()

    # send hmac
    C.send_K_digest(M)

    # brute force hmac
    M.get_password()

    # check password equality
    print M.password == C.password
    print M.password


if __name__ == "__main__":
	main_normal()
