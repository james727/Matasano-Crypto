import base64

hex_input = '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d'

def hex_to_base64(hex_input):
    return hex_input.decode('hex').encode('base64')

print hex_to_base64(hex_input)
