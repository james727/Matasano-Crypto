from os import urandom
import random
from Crypto.Cipher import AES

prepend_string= urandom(random.randint(1,100))
print len(prepend_string)
KEY = urandom(16)
target = "Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
BLOCK_SIZE = 16

def ecb_encrypt(plain_text, key):
    cipher = AES.new(key, AES.MODE_ECB)
    padded_text = pks_padding(plain_text, BLOCK_SIZE)
    cipher_text = cipher.encrypt(padded_text)
    return cipher_text.encode('hex')

def ecb_decrypt(hex_cipher_text, key):
    cipher_text = hex_cipher_text.decode('hex')
    cipher = AES.new(key, AES.MODE_ECB)
    plain_text_padded = cipher.decrypt(cipher_text)
    return pks_unpadding(plain_text_padded, BLOCK_SIZE)

def create_ciphertext(attacker_controlled):
    plaintext = prepend_string+attacker_controlled+target.decode('base64')
    return ecb_encrypt(plaintext,KEY).decode('hex')

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

def get_prepend_length():
    i = 0
    while True:
        block = 'b'+15*' '
        attacker_controlled = 'a'*i+block*2
        cipher_text = create_ciphertext(attacker_controlled)

        num_blocks = len(cipher_text)//16
        for j in range(num_blocks):
            block = cipher_text[16*j:16*(j+1)]
            next_block = cipher_text[16*(j+1):16*(j+2)]
            if block == next_block:
                return (16-i)+(j-1)*16
        i+=1

def get_next_char(prepend_length,block_size,known_leading_chars):
    block_filler = 'a'*(block_size-prepend_length%block_size)
    leading_length = block_size-1-(len(known_leading_chars)%block_size)
    current_input = block_filler+'a'*leading_length
    block_number = len(known_leading_chars)//block_size + prepend_length//block_size + 1
    block_start, block_finish = (block_number*block_size, block_number*block_size+block_size)
    output = create_ciphertext(current_input)[block_start:block_finish]
    for i in range(1,255):
        test_input = current_input+known_leading_chars+chr(i)
        cipher_text = create_ciphertext(test_input)[block_start:block_finish]
        if cipher_text == output:
            return chr(i)
    return False

if __name__ == "__main__":
    prepend_length = get_prepend_length()
    known_leading_chars = ''
    next_char = 'a'
    while next_char:
        next_char = get_next_char(prepend_length, BLOCK_SIZE, known_leading_chars)
        if next_char:
            known_leading_chars+=next_char
    print known_leading_chars
