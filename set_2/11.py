import aes_10
import random
from os import urandom
import urllib2

def random_aes_encrypt(plain_text):
    encryption_type = random.randint(1,2)
    front_padding_length = random.randint(5,10)
    back_padding_length = random.randint(5,10)
    front_padding = urandom(front_padding_length)
    back_padding = urandom(back_padding_length)
    plain_text = front_padding+plain_text+back_padding
    key = urandom(16)
    initialization_vector = None

    if encryption_type == 1: #ecb
        cipher_type = "ECB"
        cipher_text = aes_10.ecb_encrypt(plain_text, key)
    elif encryption_type == 2: #cbc
        cipher_type = "CBC"
        initialization_vector = urandom(16)
        cipher_text = aes_10.cbc_encrypt(plain_text, key, initialization_vector)

    return cipher_text, cipher_type, key, initialization_vector

def get_file_string(filename):
    contents = ""
    for line in urllib2.urlopen(filename):
        s = line.rstrip('\n')
        contents+=s
    return contents

def get_chunks(text, chunk_length):
    chunks = []
    num_chunks = len(text)//chunk_length
    for i in range(len(text)-chunk_length):
        chunk = text[i:i+chunk_length]
        chunks.append(chunk)
    return chunks

def get_ecb_score(cipher_text):
    chunk_length = 16
    indexes = range(0,len(cipher_text),chunk_length)
    d = []
    for start, end in zip(indexes, indexes[1:]):
        d.append(cipher_text[start:end])
    d_set = set(d)
    if len(d_set)<len(d):
        return "ECB"
    return "CBC"

def get_random_chunks(text):
    index = 0
    chunks = []
    while index < len(text):
        chunk_length = random.randint(64, 128)
        if index+chunk_length >= len(text):
            chunk = text[index:]
        else:
            chunk = text[index:index+chunk_length]
        index+=chunk_length
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    filename = "http://textfiles.com/100/anonymit"
    s = get_file_string(filename)
    s = 'a'*200
    s = 'b'*1000
    s_chunks = get_random_chunks(s)
    #s_chunks = [s]
    for chunk in s_chunks:
        cipher_text, cipher_type, key, iv = random_aes_encrypt(chunk)
        text_ecb_score = get_ecb_score(cipher_text)
        print cipher_type, text_ecb_score
