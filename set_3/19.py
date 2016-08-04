from Crypto.Cipher import AES
BLOCK_SIZE = 16
AES_KEY = "YELLOW SUBMARINE"

def cbc_encrypt_keystream(nonce, key):
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(nonce)
    return cipher_text

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

def generate_keystream(key, plain_text):
    needed_length = 1+len(plain_text)//16
    keystream = ''
    for i in range(needed_length):
        nonce = chr(0)*8 + chr(i) + chr(0)*7
        keystream+=cbc_encrypt_keystream(nonce, key)
    return keystream

def ctr_encrypt(plain_text, key):
    keystream = generate_keystream(key, plain_text)
    return bitwise_xor(plain_text, keystream)

def ctr_decrypt(cipher_text, key):
    return ctr_encrypt(cipher_text, key)

def get_texts():
    f = open('19_cyphertext.txt','r')
    c = []
    for line in f:
        c.append(line.rstrip().decode('base64'))
    f.close()
    return c

def encrypt_plaintexts(p):
    c = []
    for pt in p:
        c.append(ctr_encrypt(pt, AES_KEY))
    return c

def identify_spaces(ciphertexts):
    uc = []
    for c1 in ciphertexts:
        uppercase_counter = [0]*len(c1)
        for c2 in [c for c in ciphertexts if c!=c1]:
            x = bitwise_xor(c1,c2)
            for i in range(len(x)):
                if x[i].isupper():
                    uppercase_counter[i]+=1
        for i in range(len(uppercase_counter)):
            if uppercase_counter[i]>=.8*len(ciphertexts):
                uppercase_counter[i]=True
            else:
                uppercase_counter[i]=False
        uc.append(uppercase_counter)
    return uc

def update_stream(ciphertexts, spaces, current_guess):
    cg_list = list(current_guess)
    for i in range(len(ciphertexts)):
        ct = ciphertexts[i]
        s = spaces[i]
        for j in range(len(s)):
            if s[j]:
                cg_list[j] = chr(ord(ct[j])^ord(' '))
    return ''.join(cg_list)

def update_for_char(ciphertexts, cipher_no, char_no, char_value, current_guess):
    cg_list = list(current_guess)
    c = ciphertexts[cipher_no]
    key_value = chr(ord(c[char_no])^ord(char_value))
    cg_list[char_no] = key_value
    return ''.join(cg_list)

def print_cipher_for_key_guess(cyphertexts, current_guess):
    for c in cyphertexts:
        cd = ''
        for i in range(len(c)):
            cc = c[i]
            kt = current_guess[i]
            if kt != '0':
                cd+=chr(ord(kt)^ord(cc))
            else:
                cd+='_'
        print cd



if __name__ == "__main__":
    c = get_texts()
    c_crypt = encrypt_plaintexts(c)
    common_length = min([len(x) for x in c_crypt])
    c_crypt = [x[:common_length] for x in c_crypt]
    spaces = identify_spaces(c_crypt)
    current_guess = update_stream(c_crypt, spaces, '0'*common_length)
    current_guess = update_for_char(c_crypt, -1, 4, 'r', current_guess)
    current_guess = update_for_char(c_crypt, -2, -5, 'e', current_guess)
    current_guess = update_for_char(c_crypt, -3, -8, ' ', current_guess)
    current_guess = update_for_char(c_crypt, -3, -9, 's', current_guess)
    current_guess = update_for_char(c_crypt, -2, -10, 'd', current_guess)
    current_guess = update_for_char(c_crypt, -12, 3, 's', current_guess)
    current_guess = update_for_char(c_crypt, -9, 2, 'd', current_guess)
    current_guess = update_for_char(c_crypt, -10, 0, 't', current_guess)
    print_cipher_for_key_guess(c_crypt, current_guess)

    # This only gets the first (min(len(x)) for x in lines) characters of each line.
    # By googling, it's clear that the plain text is: http://www.shmoop.com/easter-1916/poem-text.html
