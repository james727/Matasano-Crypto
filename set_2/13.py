from Crypto.Cipher import AES
from os import urandom

key = urandom(16)
BLOCK_SIZE = 16

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

def k_v_parsing(cookie):
    cookies = cookie.split('&')
    return {key:value for key,value in [x.split('=') for x in cookies]}

def profile_for(email):
    email = email.strip('&')
    email = email.strip('=')
    return ecb_encrypt("email="+email+"&uid="+"10"+"&role="+"user",key)

def get_block_size():
    old_length = len(profile_for('').decode('hex'))
    for i in range(50):
        email = 'a'*i
        cipher = profile_for(email).decode('hex')
        length = len(cipher)
        if length != old_length:
            return i-1, length-old_length
    return False

def get_admin_ciphertext():
    for i in range(16):
        input_string = 'a'*i+pks_padding('admin',16)
        ct = profile_for(input_string).decode('hex')
        if len(ct)>16:
            block2=ct[16:32]
            if ecb_decrypt(block2.encode('hex'),key)=='admin':
                return block2
    return False

if __name__ == "__main__":
    input_string_length, block_size = get_block_size()
    # get input string to leave 'user' hanging off the end
    new_length = input_string_length+len('user')
    cipher_text = profile_for('a'*(new_length+1)).decode('hex')
    first_two_blocks = cipher_text[:len(cipher_text)-16]
    admin_block = get_admin_ciphertext()

    # smash together
    final_cipher = first_two_blocks+admin_block
    print pks_unpadding(ecb_decrypt(final_cipher.encode('hex'),key),16)
