import aes_10
import random
from os import urandom
import urllib2

random_key = urandom(16)

def pks_padding(plain_text, block_size):
    final_block_length = len(plain_text)%block_size
    padding_needed = block_size-final_block_length
    hex_escape = "\\x{:02x}".format(padding_needed)
    return plain_text+hex_escape*padding_needed

def ecb_encrypt(plain_text,key):
    ending = "Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
    plain_text= plain_text+ending.decode('base64')
    cipher_text = aes_10.ecb_encrypt(plain_text, key)
    return cipher_text

def encryption_oracle(cipher_text):
    chunk_length = 16
    indexes = range(0,len(cipher_text),chunk_length)
    d = []
    for start, end in zip(indexes, indexes[1:]):
        d.append(cipher_text[start:end])
    d_set = set(d)
    if len(d_set)<len(d):
        return "ECB"
    return "CBC"

def detect_block_size(encryption_method,key):
    old_cipher_text_length = len(encryption_method('a',key))
    new_cipher_text_length = len(encryption_method('a'*2,key))
    i = 3
    while new_cipher_text_length == old_cipher_text_length:
        old_cipher_text_length = new_cipher_text_length
        new_cipher_text_length = len(encryption_method('a'*i,key))
        i+=1
    return new_cipher_text_length-old_cipher_text_length

def get_next_char(block_size,known_leading_chars):
    leading_length = block_size-1-(len(known_leading_chars)%block_size)
    current_input = 'a'*leading_length
    block_number = len(known_leading_chars)//block_size
    block_start, block_finish = (block_number*block_size, block_number*block_size+block_size)
    output = ecb_encrypt(current_input, random_key)[block_start:block_finish]
    for i in range(1,255):
        test_input = current_input+known_leading_chars+chr(i)
        cipher_text = ecb_encrypt(test_input, random_key)[block_start:block_finish]
        if cipher_text == output:
            return chr(i)
    return False


if __name__ == "__main__":
    s = "a"*1000
    block_size = detect_block_size(ecb_encrypt, random_key)
    mode_of_operation = encryption_oracle(ecb_encrypt(s,random_key))
    known_leading_chars = ''
    next_char = 'a'
    while next_char:
        next_char = get_next_char(block_size, known_leading_chars)
        if next_char:
            known_leading_chars+=next_char
    print known_leading_chars
