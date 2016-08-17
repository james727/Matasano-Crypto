import sha1_2
from os import urandom

def sha_hash(ct, key):
    h = sha1.Sha1Hash()
    h.update(key+ct)
    return h.hexdigest()

def get_registers(hexdigest):
    return [hexdigest[8*i:8*(i+1)] for i in range(5)]


def get_int(chars):
    b = ''.join([bin(ord(x))[2:].zfill(8) for x in chars])
    return int(b, 2)

def sha_padding(ct, key):
    h = sha1.Sha1Hash()
    h.update(key+ct)
    d = h.digest()
    return h.message

def md_padding(message):
    num_bits = 8*len(message)
    mod = num_bits%512

    # pad to 448
    if mod < 448:
        delta = 448-mod
        chars = delta/8
        message += chr(128)+'\0'*(chars-1)
    elif mod > 448:
        delta = 512-mod+448
        chars = delta/8
        message += chr(128) + '\0'*(chars-1)

    # pad with message length
    length = num_bits
    message+=hex_escape_64(length)

    return message

def hex_escape_64(n):
    b = format(n, 'b').zfill(64)
    o = ''
    for i in range(8):
        n = b[8*i:8*(i+1)]
        o+=chr(int(n,2))
    return o

def test_padding():
    sha = sha1.Sha1Hash()
    message = "I am a god, plain and simple."
    key = urandom(16)
    my_padding = md_padding(key + message)
    test_padding = sha_padding(message, key)
    print len(my_padding)
    print len(test_padding)
    for i in range(len(my_padding)):
        print ord(my_padding[i]), ord(test_padding[i])

def set_registers_and_get_digest(hex_registers, new_text):
    int_regs = [int(x, 16) for x in hex_registers]
    h = sha1_2.SHA1()
    h._SHA1__H = int_regs
    h.update(new_text, falsify = True)
    return h.hexdigest()

if __name__ == "__main__":
    key = urandom(16)
    ct = "comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"
    hasher = sha1_2.SHA1()
    hasher.update(key+ct)
    digest1 = hasher.hexdigest()
    registers = get_registers(digest1)

    cookie = ";admin=true"
    old_message = md_padding(key+ct)
    test_message = old_message + cookie

    h_test = sha1_2.SHA1()
    h_test.update(test_message)
    test_digest = h_test.hexdigest()

    digest_forged = set_registers_and_get_digest(registers, cookie)

    print test_digest
    print digest_forged
