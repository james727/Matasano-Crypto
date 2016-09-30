from RC4_cipher import RC4
from os import urandom
import time
from Crypto.Cipher import ARC4

NUM_ITERATIONS = 2**25

def RC4_keystream(key, length):
    cipher = ARC4.new(key)
    plaintext = chr(0) * length
    return cipher.encrypt(plaintext)

def RC4_encrypt(key, text):
    cipher = ARC4.new(key)
    return cipher.encrypt(text)

def test_pycrypto_bias():
    # Tests the byte 16 biases for fun and profit
    counter = {i: 0 for i in range(256)}

    for i in xrange(2**25):
        key = urandom(16)
        keystream = RC4_keystream(key, 16)
        byte_16 = keystream[-1]
        counter[ord(byte_16)]+=1

    top_bytes = sorted([(byte, count) for byte, count in counter.items()], reverse = True, key = lambda x: x[1])
    for byte, count in top_bytes:
        print str(byte) + ", " + str(count)


def test_vector_pycrypto():
    key = "0102030405".decode('hex')
    target_stream = "".join("b2 39 63 05  f0 3d c0 27   cc c3 52 4a  0a 11 18 a8".split()).decode('hex')
    keystream = RC4_keystream(key, len(target_stream))
    assert keystream == target_stream

def test_biases():
    # Tests the byte 16 biases for fun and profit
    counter = {i: 0 for i in range(256)}
    cipher = RC4("a"*256)

    for i in xrange(10000):
        key = urandom(256)
        cipher.set_key(key)
        keystream = cipher.gen_keystream(16)
        byte_16 = keystream[-1]
        counter[ord(byte_16)] += 1

    top_bytes = sorted([(key, count) for key, count in counter.items()], reverse = True, key = lambda x: x[1])

    print "The most frequent bytes are:"
    for byte, count in top_bytes[:20]:
        print str(byte) + ": " + str(count)

def submit_form(txt):
    cookie = "QkUgU1VSRSBUTyBEUklOSyBZT1VSIE9WQUxUSU5F".decode('base64')
    key = urandom(16)
    full_plaintext = txt + cookie
    return RC4_encrypt(key, full_plaintext)

def get_cookie_length():
    txt = ""
    ciphertext = submit_form(txt)
    return len(ciphertext)

def get_max_freq_byte(prefix_txt, byte_index):
    out = {i: 0 for i in range(256)}
    for i in range(NUM_ITERATIONS):
        ciphertext = submit_form(prefix_txt)
        biased_byte = ord(ciphertext[byte_index])
        out[biased_byte] += 1
    return max(out.keys(), key = lambda x: out[x])

def get_next_cookie_character(i):
    if i <= 15:
        max_freq_byte = 240
        byte_index = 15
    elif i <= 31:
        max_freq_byte = 224
        byte_index = 31
    prefix = " " * (byte_index - i)
    max_freq_cipher_byte = get_max_freq_byte(prefix, byte_index)
    char = chr(max_freq_byte ^ max_freq_cipher_byte)
    if ord(char) > 177:
        raise Exception("Invalid character")
    return char

def RC4_bias_attack():
    cookie_length = get_cookie_length()
    cookie = ""
    for i in range(cookie_length):
        cookie += get_next_cookie_character(i)
        print cookie
    return cookie

if __name__ == "__main__":
    cookie = RC4_bias_attack()
    t0 = time.time()
    test_pycrypto_bias()
    print "Execution time: " + str((time.time()-t0)/1000)
