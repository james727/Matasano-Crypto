from os import urandom
import random
from Crypto.Cipher import AES
import zlib
import itertools

BLOCK_SIZE = 16

def pks_padding(plain_text, block_size):
    final_block_length = len(plain_text)%block_size
    padding_needed = block_size-final_block_length
    hex_escape = chr(padding_needed)
    return plain_text+hex_escape*padding_needed

def cbc_encrypt(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pks_padding(plain_text, BLOCK_SIZE)
    cipher_text = cipher.encrypt(padded_text)
    return cipher_text

def format_request(p):
    r = "POST / HTTP/1.1 Host: hapless.com Cookie: sessionid=TmV2ZXIgcmV2ZWFsIHRoZSBXdS1UYW5nIFNlY3JldCE= Content-Length: (({0})) (({1}))".format(len(p), p)
    return r

def oracle(p):
    k = urandom(BLOCK_SIZE)
    iv = urandom(BLOCK_SIZE)
    f = format_request(p)
    comp = zlib.compress(f)
    c = cbc_encrypt(comp, k, iv)
    return len(c)

def get_compression_ratio(m):
    return (0.0 + oracle(m) - oracle(""))/len(m)

def get_block_modulus(chars):
    current_length = oracle(chars)
    cntr = 0
    while True:
        chars = str(cntr) + chars
        new_length = oracle(chars)
        if new_length > current_length:
            return cntr
        cntr+=1

def get_base64_nums():
    a = range(97,123) + range(65, 91) + range(48, 58) + [43, 47, 32, 61]
    return [chr(x) for x in a]

def get_base64_combos():
    a = range(97,123) + range(65, 91) + range(48, 58) + [43, 47, 32, 61]
    b = itertools.product(a, a)
    c = [str(chr(x[0])) + str(chr(x[1])) for x in b]
    return c

def get_next_2_options(options):
    #o = []
    d = {}
    for option in options:
        block_missing_chars = get_block_modulus(option)
        leading_chars = ''.join([str(x) for x in range(block_missing_chars)])[:-1]
        padded_option = leading_chars + option
        for c in get_base64_combos():
            m = option +  c
            padded_m = padded_option + c
            padding_needed = get_block_modulus(m)
            try:
                d[padding_needed].append(m)
            except:
                d[padding_needed] = [m]
    new_options = d[max(d.keys())]
    candidates = [x[-2] for x in new_options]
    counts = {x: len([y for y in new_options if y[-2] == x]) for x in candidates}
    best_option = max(counts.keys(), key = lambda x: counts[x])
    sorted_options = sorted(counts.keys(), key = lambda x: counts[x], reverse = True)
    return [option + best_option for option in options]

def get_next_options(options):
    o = []
    for option in options:
        block_missing_chars = get_block_modulus(option)
        print option
        leading_chars = ''.join([str(x) for x in range(block_missing_chars)])
        padded_option = leading_chars + option
        for c in get_base64_nums():
            m = option +  c
            padded_m = padded_option + c
            o.append((m, get_block_modulus(m)))

    best_score = max(o, key = lambda x: x[1])[1]
    sorted_options = sorted(o, key = lambda x: x[1], reverse = True)
    new_options = [x[0] for x in o if x[1] == best_score]
    if len(new_options)< 10:
        return new_options
    else:
        return get_next_2_options(options)

def check_characters():
    o = []
    m0 = "Cookie: sessionid="
    options = [m0]
    i = 0
    while len([x for x in options if "Content" in x]) == 0:
        new_options = set(get_next_options(options))
        options = new_options
    options = list(options)
    cookie = options[0].split(" ")[1][len("sessionid="):]
    print "The session cookie is: " + cookie

if __name__ == "__main__":
    check_characters()
