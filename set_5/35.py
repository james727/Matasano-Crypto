import random, hashlib, sys
from Crypto.Cipher import AES
from os import urandom

BLOCK_SIZE = 16
sys.setrecursionlimit(3000)

def modExp(base, exp, p):
	if exp == 1: return base%p
	if exp%2 == 0: return (modExp(base, exp//2, p)**2)%p
	else: return (modExp(base, 1, p)*modExp(base, exp - 1, p))%p

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
	def __init__(self):
		self.p = int('ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff',16)
		self.g = None
		self.pk1 = None
		self.pk2 = None

	def modify_G(self, A, B, g):
		A.g = g
		B.g = g

	def get_key(self, g):
		if g == 1:
			return 1
		elif g == self.p:
			return 0
		elif g == self.p-1:
			return self.p-1

	def get_message(self, counterpart, g):
		self.generate_session_key(self.get_key(g))
		plain_text = decrypt_aes_cbc(counterpart.public_message, self.session_key, counterpart.public_message[-16:])
		return pks_unpadding(plain_text[:-16], BLOCK_SIZE)

	def generate_session_key(self, s):
		n = hashlib.sha256()
		n.update(str(s).encode('utf-8'))
		self.session_key = n.digest()[0:16]

class diffie_party(object):
	def __init__(self):
		self.p = int('ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff',16)
		self.g = 2
		self.private_key = random.randint(1, self.p)
		self.session_key = None

	def generate_public_key(self):
		self.public_key = modExp(self.g, self.private_key, self.p)

	def accept_session(self, counterpart):
		self.p = counterpart.p
		self.g = counterpart.g
		self.generate_session_key(counterpart.get_public_key())

	def generate_session_key(self, pk_counterpart):
		n = hashlib.sha256()
		s = modExp(pk_counterpart, self.private_key, self.p)
		n.update(str(s).encode('utf-8'))
		self.session_key = n.digest()[0:16]

	def get_public_key(self):
		return self.public_key

	def broadcast_message(self, message):
		iv = urandom(16)
		self.public_message = encrypt_aes_cbc(pks_padding(message, BLOCK_SIZE), self.session_key, iv) + iv

	def get_message(self, counterpart):
		plain_text = decrypt_aes_cbc(counterpart.public_message[:-16], self.session_key, counterpart.public_message[-16:])
		return pks_unpadding(plain_text[:-16], BLOCK_SIZE)

def uninterrupted_communication():
    A = diffie_party()
    B = diffie_party()
    B.accept_session(A)
    A.generate_session_key(B.get_public_key())

    m1 = "omgomgomg top-notch crypto"
    m2 = "thx m8 ily 2"

    A.broadcast_message(m1)
    print B.get_message(A)

def haxored_communication():
    # create parties
	A = diffie_party()
	B = diffie_party()
	M = mitm_haxor()
	M.modify_G(A,B,1)
	A.generate_public_key()
	B.generate_public_key()

    # key transfer
	B.accept_session(A)
	A.generate_session_key(B.get_public_key())

    # set up messages
	ma = "omg i'm gonna sneak this by u M8"
	mb = "got ur msg m8 we're rly sneaky"

    # broadcast messages
	A.broadcast_message(ma)
	B.broadcast_message(mb)

    # decrypt
	print "---Decryption of messages using g = 1---"
	print M.get_message(A, 1)
	print M.get_message(B, 1)+"\n"

	A = diffie_party()
	B = diffie_party()
	M.modify_G(A,B,M.p)
	A.generate_public_key()
	B.generate_public_key()
	B.accept_session(A)
	A.generate_session_key(B.get_public_key())
	A.broadcast_message(ma)
	B.broadcast_message(mb)

	# decrypt
	print "---Decryption of messages using g = p---"
	print M.get_message(A, M.p)
	print M.get_message(B, M.p)+"\n"

	A = diffie_party()
	B = diffie_party()
	M.modify_G(A,B,M.p-1)
	A.generate_public_key()
	B.generate_public_key()
	B.accept_session(A)
	A.generate_session_key(B.get_public_key())
	A.broadcast_message(ma)
	B.broadcast_message(mb)

	# decrypt
	print "---Decryption of messages using g = p-1---"
	print "---Test 1 - try key = p-1---"
	print M.get_message(A, M.p-1)
	print M.get_message(B, M.p-1)+"\n"

	# decrypt
	print "---Decryption of messages using g = p-1---"
	print "---Test 1 - try key = 1---"
	print M.get_message(A, 1)
	print M.get_message(B, 1)



if __name__ == "__main__":
    haxored_communication()
