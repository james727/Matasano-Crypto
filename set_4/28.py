import sha1
from os import urandom

def hash(ct, key):
    h = sha1.Sha1Hash()
    h.update(key+ct)
    return h.digest()

if __name__ == "__main__":
    key = urandom(16)
    ct = urandom(128)
    h1 = hash(ct, key)
    h2 = hash(ct, key+'a')
    print h1 == h2
