from os import urandom
import random
from Crypto.Cipher import AES

RANDOM_KEY = "YELLOW SUBMARINE"
BLOCK_SIZE = 16

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

def cbc_encrypt_unpadded(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(plain_text)
    return cipher_text

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

def cbc_mac(m, iv):
    c = cbc_encrypt(m, RANDOM_KEY, iv)
    return c[-16:].encode('hex')

def test():
    message = "alert('MZA who was that?');\n"
    iv = '\0'*16
    assert cbc_mac(message, iv) == "296b8d7cb78a243dda4d0a61d33bbdd1"
    to_forge = "296b8d7cb78a243dda4d0a61d33bbdd1"

    new_message = "alert('Ayo, the Wu is back' );//"
    mac = cbc_encrypt_unpadded(new_message, RANDOM_KEY, iv)[-16:]

    old_ct = cbc_encrypt(message, RANDOM_KEY, iv)
    E = old_ct[-32:-16]
    old_pt = pks_padding(message, BLOCK_SIZE)
    P = old_pt[-16:]
    new_m = bitwise_xor(bitwise_xor(P, E), mac)

    forged_m = new_message + new_m
    new_mac = cbc_encrypt_unpadded(forged_m, RANDOM_KEY, iv)[-16:].encode('hex')
    assert new_mac == to_forge
    print forged_m

if __name__ == "__main__":
    test()
