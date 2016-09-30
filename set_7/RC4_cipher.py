# Implementation of the RC4 stream cipher. Implemented for use in challenge 56

class RC4(object):
    def __init__(self, key):
        # Key must be 256 bytes (for speed)
        self.key = key
        self.keylength = len(key)
        self.KSA()

    def KSA(self):
        # Permutes the internal state according to self.key
        S = [i for i in range(256)]
        j = 0

        for i in range(256):
            j = (j + S[i] + ord(self.key[i])) % 256
            S[i], S[j] = S[j], S[i]

        self.S = S

    def set_key(self, key):
        self.key = key
        self.keylength = len(key)
        self.KSA()

    def gen_keystream(self, stream_length):
        # Generates a keystream of length stream_length
        i = 0
        j = 0
        out = ""

        while len(out) < stream_length:
            i = (i + 1) % 256
            j = (j + self.S[i]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i]
            K_byte = self.S[(self.S[i] + self.S[j]) % 256]
            out += chr(K_byte)

        return out

    def bitwise_xor(self, x, y):
        # Bitwise xor of two strings x and y
        return ''.join([chr(ord(x[i]) ^ ord(y[i])) for i in range(len(x))])

    def transform(self, txt):
        # Takes a plaintext/ciphertext and encrypts/decrypts
        self.KSA()
        key_stream = self.gen_keystream(len(txt))
        return self.bitwise_xor(txt, key_stream)

def tests():
    # 2 simple tests; 1 checking if D(C(x)) = x and the other validating against
    # a test vector from the RC4 RFC.
    key = "YELLOW SUBMARINE"
    cipher = RC4(key)
    text = "I like cheese"
    assert cipher.transform(cipher.transform(text)) == text

    key = "0102030405".decode('hex')
    cipher = RC4(key)
    target_stream = "".join("b2 39 63 05  f0 3d c0 27   cc c3 52 4a  0a 11 18 a8".split()).decode('hex')
    assert cipher.gen_keystream(len(target_stream)) == target_stream

if __name__ == "__main__":
    tests()
