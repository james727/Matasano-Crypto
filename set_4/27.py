from os import urandom
import random
from Crypto.Cipher import AES

RANDOM_KEY = urandom(16)
iv = urandom(16)
BLOCK_SIZE = 16

def final_string(input_text):
    s1 = "comment1=cooking%20MCs;userdata="
    s2 = ";comment2=%20like%20a%20pound%20of%20bacon"
    cleaned_input = ''.join(input_text.split(';'))
    cleaned_input = ''.join(cleaned_input.split('='))
    return s1+cleaned_input+s2

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

def valid_padding(plain_text, block_size):
    last_chr = plain_text[-1]
    if ord(last_chr) < block_size:
        t_list = list(plain_text)
        c = 0
        while c<ord(last_chr):
            if ord(t_list[-1])!=ord(last_chr):
                raise Exception('Improper PKCS#7 padding')
            t_list.pop(-1)
            c+=1
        return ''.join(t_list)
    else:
        return plain_text

def cbc_encrypt(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pks_padding(plain_text, BLOCK_SIZE)
    cipher_text = cipher.encrypt(padded_text)
    return cipher_text

def cbc_decrypt(cipher_text, key, iv):
    cipher_text = cipher_text
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text_padded = cipher.decrypt(cipher_text)
    return pks_unpadding(plain_text_padded, BLOCK_SIZE)

def process_input(input_text):
    plain_text = final_string(input_text)
    cipher_text = ctr_encrypt(plain_text, RANDOM_KEY)
    return cipher_text

def cbc_encrypt_keystream(nonce, key):
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(nonce)
    return cipher_text

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

def check_for_admin(ct):
    plain_text = ctr_decrypt(ct, RANDOM_KEY)
    tuples = [x.split('=') for x in plain_text.split(';')]
    for key, value in tuples:
        if key=='admin' and value =='true':
            return True
    return False

def check_ct_for_ascii(ct):
    pt = cbc_decrypt(ct, RANDOM_KEY, RANDOM_KEY)
    s = [x for x in pt if ord(x) >= 130]
    return True if len(s) == 0 else pt

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

if __name__ == "__main__":
    input_string = "a"*16+"b"*16+"c"*16
    ct = cbc_encrypt(input_string, RANDOM_KEY, RANDOM_KEY)
    ct = (ct[:16]+'\0'*16+ct[:16])
    s = check_ct_for_ascii(ct)
    key_guess = bitwise_xor(s[:16], s[32:])
    print key_guess.encode('hex')
    print key_guess == RANDOM_KEY
