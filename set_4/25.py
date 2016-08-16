from Crypto.Cipher import AES
from os import urandom
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

def get_file_string():
    s = ''
    with open('25_data.txt','r') as f:
        for line in f:
            s+=line.strip()
    return s

def update(ct, key, offset, new_text):
    pt = ctr_decrypt(ct, key)
    ptp = pt[:offset]+new_text
    return ctr_encrypt(ptp, key)

if __name__ == "__main__":
    cipher = AES.new("YELLOW SUBMARINE", AES.MODE_ECB)
    s = cipher.decrypt(get_file_string().decode('base64'))
    key = urandom(16)
    ct = ctr_encrypt(s, key)
    ct2 = update(ct, key, 0, '\0'*len(ct))
    print bitwise_xor(ct, ct2)
