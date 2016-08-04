import base64

s1 = 0x1c0111001f010100061a024b53535009181c

def hex_to_base64(hex_input):
    return hex_input.decode('hex').encode('base64')

def fixed_xor(s1):
    s2 = 0x686974207468652062756c6c277320657965
    xo = s1^s2
    return str(hex(xo))[2:-1]

print fixed_xor(s1)
