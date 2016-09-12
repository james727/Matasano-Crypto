from os import urandom
import random
from Crypto.Cipher import AES
from Crypto.Util import Counter
import zlib

BLOCK_SIZE = 16

def aes_ctr(m, k):
    ctr = Counter.new(128, initial_value = 1)
    cipher = AES.new(k, AES.MODE_CTR, counter = ctr)
    c = cipher.encrypt(m)
    return c

def test():
    k = urandom(16)
    m = "rehwiroewhfiosefaaaaaaaaaakfjdkfjdaji loike chees opmg djfhjs"
    c = aes_ctr(m, k)
    mp = aes_ctr(c, k)
    assert mp == m

    z = zlib.compress(m, 9)
    assert len(z) < len(m)

def format_request(p):
    r = "POST / HTTP/1.1 Host: hapless.com Cookie: sessionid=TmV2ZXIgcmV2ZWFsIHRoZSBXdS1UYW5nIFNlY3JldCE= Content-Length: (({0})) (({1}))".format(len(p), p)
    return r

def oracle(p):
    k = urandom(BLOCK_SIZE)
    f = format_request(p)
    comp = zlib.compress(f)
    c = aes_ctr(comp, k)
    return len(c)

def get_compression_ratio(m):
    return (0.0 + oracle(m) - oracle(""))/len(m)

def get_next_characters(chars):
    o = []
    for i in range(255):
        o.append((chr(i), get_compression_ratio(chars + chr(i))))
    best_score =  min(o, key = lambda x: x[1])[1]
    return [x[0] for x in o if x[1] == best_score]

def get_next_options(options):
    o = []
    for option in options:
        for i in range(255):
            m = option + chr(i)
            o.append((m, get_compression_ratio(m)))
    best_score = min(o, key = lambda x: x[1])[1]
    return [x[0] for x in o if x[1] == best_score]

def check_characters():
    o = []
    m0 = "sessionid="
    options = [m0]
    i = 0
    while len([x for x in options if "Content" in x]) == 0:
        options = set(get_next_options(options))
        print options
    cookie = [x for x in options if "Content" in x][0].split(" ")[0][len(m0):]
    print "The session cookie is: " + cookie

if __name__ == "__main__":
    test()
    check_characters()
