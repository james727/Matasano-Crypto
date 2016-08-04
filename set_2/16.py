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
    return cipher_text.encode('hex')

def cbc_decrypt(hex_cipher_text, key, iv):
    cipher_text = hex_cipher_text.decode('hex')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text_padded = cipher.decrypt(cipher_text)
    return pks_unpadding(plain_text_padded, BLOCK_SIZE)

def process_input(input_text):
    plain_text = final_string(input_text)
    cipher_text = cbc_encrypt(plain_text, RANDOM_KEY, iv)
    return cipher_text

def check_for_admin(hex_cipher_text):
    plain_text = cbc_decrypt(hex_cipher_text, RANDOM_KEY, iv)
    tuples = [x.split('=') for x in plain_text.split(';')]
    for key, value in tuples:
        if key=='admin' and value =='true':
            return True
    return False

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

if __name__ == "__main__":
    user_input = chr(0)*32
    ct = process_input(user_input).decode('hex')
    block_to_manipulate = ct[32:48]
    desired_output = ';admin=true;'+chr(0)*(16-len(';admin=true;'))
    new_block = bitwise_xor(desired_output,block_to_manipulate)
    new_ct = ct[:32]+new_block+ct[48:]
    print check_for_admin(new_ct.encode('hex'))
