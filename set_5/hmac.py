import sha1_2

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

def hmac(key, message):
    h = sha1_2.SHA1()
    if len(key) > 64:
        key = h.update(key).hexdigest()
    elif len(key)<64:
        key = key + '\0'*(64-len(key))

    o_key_pad = bitwise_xor('\\'*64, key)
    i_key_pad = bitwise_xor('6'*64, key)

    h = sha1_2.SHA1()
    h.update(i_key_pad+message)
    tmp_digest = h.hexdigest()
    h = sha1_2.SHA1()
    h.update(o_key_pad + tmp_digest)
    return h.hexdigest()
