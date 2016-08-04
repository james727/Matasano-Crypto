from Crypto.Cipher import AES
BLOCK_SIZE = 16
AES_KEY = "YELLOW SUBMARINE"

def cbc_encrypt_keystream(nonce, key):
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(nonce)
    return cipher_text

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

def generate_keystream(key, plain_text):
    needed_length = 1+len(plain_text)//16
    keystream = ''
    for i in range(needed_length):
        nonce = chr(0)*8 + chr(i) + chr(0)*7
        keystream+=cbc_encrypt_keystream(nonce, key)
    return keystream

def ctr_encrypt(plain_text, key):
    keystream = generate_keystream(key, plain_text)
    return bitwise_xor(plain_text, keystream)

def ctr_decrypt(cipher_text, key):
    return ctr_encrypt(cipher_text, key)

if __name__ == "__main__":
    a ="L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ==".decode('base64')
    print ctr_decrypt(a, AES_KEY)
