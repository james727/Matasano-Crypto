from os import urandom
import random
from Crypto.Cipher import AES
RANDOM_KEY = urandom(16)
INITIALIZATION_VECTOR = urandom(16)
BLOCK_SIZE = 16

s_list = ['MDAwMDAwTm93IHRoYXQgdGhlIHBhcnR5IGlzIGp1bXBpbmc=',
    'MDAwMDAxV2l0aCB0aGUgYmFzcyBraWNrZWQgaW4gYW5kIHRoZSBWZWdhJ3MgYXJlIHB1bXBpbic=',
    'MDAwMDAyUXVpY2sgdG8gdGhlIHBvaW50LCB0byB0aGUgcG9pbnQsIG5vIGZha2luZw==',
    'MDAwMDAzQ29va2luZyBNQydzIGxpa2UgYSBwb3VuZCBvZiBiYWNvbg==',
    'MDAwMDA0QnVybmluZyAnZW0sIGlmIHlvdSBhaW4ndCBxdWljayBhbmQgbmltYmxl',
    'MDAwMDA1SSBnbyBjcmF6eSB3aGVuIEkgaGVhciBhIGN5bWJhbA==',
    'MDAwMDA2QW5kIGEgaGlnaCBoYXQgd2l0aCBhIHNvdXBlZCB1cCB0ZW1wbw==',
    'MDAwMDA3SSdtIG9uIGEgcm9sbCwgaXQncyB0aW1lIHRvIGdvIHNvbG8=',
    'MDAwMDA4b2xsaW4nIGluIG15IGZpdmUgcG9pbnQgb2g=',
    'MDAwMDA5aXRoIG15IHJhZy10b3AgZG93biBzbyBteSBoYWlyIGNhbiBibG93']

def get_cipher_text():
    s = random.choice(s_list)
    ct = cbc_encrypt(s, RANDOM_KEY, INITIALIZATION_VECTOR)
    return ct

def padding_valid(hex_cipher_text):
    pt_padded = cbc_decrypt(hex_cipher_text, RANDOM_KEY, INITIALIZATION_VECTOR)
    return valid_padding(pt_padded,BLOCK_SIZE)

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
    if ord(last_chr) <= block_size and ord(last_chr)>0:
        t_list = list(plain_text)
        c = 0
        while c<ord(last_chr):
            if ord(t_list[-1])!=ord(last_chr):
                #raise Exception('Improper PKCS#7 padding')
                return False
            t_list.pop(-1)
            c+=1
        return ''.join(t_list)
    else:
        return False

def cbc_encrypt(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pks_padding(plain_text, BLOCK_SIZE)
    cipher_text = cipher.encrypt(padded_text)
    return cipher_text.encode('hex')

def cbc_decrypt(hex_cipher_text, key, iv):
    cipher_text = hex_cipher_text.decode('hex')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(cipher_text)

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

def get_blocks(text):
    num_blocks = len(text)/BLOCK_SIZE
    blocks = [text[BLOCK_SIZE*i:BLOCK_SIZE*(i+1)] for i in range(num_blocks)]
    return blocks

def get_next_char(cyphertext, known_chars):
    # get correct set of blocks and spillover_chars
    blocks = get_blocks(cyphertext)
    #print "PRINTING BLOCKS..."
    #print blocks
    num_blocks_filled = len(known_chars)//BLOCK_SIZE
    #print "Blocks filled = " + str(num_blocks_filled)
    remaining_blocks = blocks[:len(blocks)-num_blocks_filled]
    len_spillover = len(known_chars)%BLOCK_SIZE
    #print "Spillover length = "+str(len_spillover)
    spillover_chars = known_chars[:len_spillover]

    # fill spillover_chars
    target_padding_number = len(spillover_chars)+1
    #print "Target padding number = "+str(target_padding_number)
    target_block_list = list(remaining_blocks[-2])
    #print target_block_list
    for index, char in enumerate(spillover_chars):
        block_index = BLOCK_SIZE-len_spillover+index
        target_ct_char = target_block_list[block_index]
        target_block_list[block_index] = chr(ord(target_ct_char)^ord(char)^target_padding_number)

    # set target index and test through iteration!!
    target_index = BLOCK_SIZE-len_spillover-1
    #print "Target index = "+str(target_index)
    old_val = ord(target_block_list[target_index])
    for z in range(255):
        target_block_list[target_index] = chr(old_val^z^target_padding_number)
        new_block = ''.join(target_block_list)
        remaining_blocks[-2] = new_block
        new_ct = ''.join(remaining_blocks).encode('hex')
        if len_spillover == 0:
            if padding_valid(new_ct) and z != target_padding_number:
                return chr(z)+known_chars
        else:
            if padding_valid(new_ct):
                return chr(z)+known_chars

if __name__ == "__main__":
    for s in s_list:
        print s.decode('base64')
    ct = get_cipher_text().decode('hex')
    end_chars = len(ct)
    ct = INITIALIZATION_VECTOR+ct
    known_chars = ''
    for i in range(end_chars):
        known_chars = get_next_char(ct, known_chars)
    print known_chars.decode('base64')
