import md4
from os import urandom
from struct import pack

def get_registers(hexdigest):
    tmp = [hexdigest[8*i:8*(i+1)] for i in range(4)]
    return [int(flip(x), 16) for x in tmp]

def flip(hex_text):
    o = ''
    for i in range(3,-1,-1):
        current_chars = hex_text[2*i:2*(i+1)]
        o+=current_chars
    return o

def md4_pad(msg):
	n = len(msg)
	bit_len = n * 8
	index = (bit_len >> 3) & 0x3fL
	pad_len = 120 - index
	if index < 56:
		pad_len = 56 - index
	padding = '\x80' + '\x00'*63
	padded_msg = msg + padding[:pad_len] + pack('<Q', bit_len)
	return padded_msg

def set_registers_and_get_digest(registers, new_text):
    h = md4.MD4()
    h.A = registers[0]
    h.B = registers[1]
    h.C = registers[2]
    h.D = registers[3]
    h.update(new_text, falsify = True)
    return h.digest()

if __name__ == "__main__":
    key = urandom(16)
    ct = "comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"
    hasher = md4.MD4()
    hasher.update(key+ct)
    digest1 = hasher.digest()
    A, B, C, D = get_registers(digest1)

    cookie = ";admin=true"
    old_message = md4_pad(key+ct)
    test_message = old_message + cookie

    h_test = md4.MD4()
    h_test.update(test_message)
    test_digest = h_test.digest()
    print "made it to digest"
    digest_forged = set_registers_and_get_digest([A,B,C,D], cookie)

    print test_digest
    print digest_forged
