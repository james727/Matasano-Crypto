from os import urandom
import random
from Crypto.Cipher import AES

RANDOM_KEY = urandom(16)
BLOCK_SIZE = 16

def pks_padding(plain_text, block_size):
    final_block_length = len(plain_text)%block_size
    padding_needed = block_size-final_block_length
    hex_escape = chr(padding_needed)
    if padding_needed == block_size:
        return plain_text
    return plain_text+hex_escape*padding_needed

def pks_unpadding(plain_text, block_size):
    last_chr = plain_text[-1]
    if ord(last_chr) < block_size:
        return plain_text[:len(plain_text)-ord(last_chr)]
    else:
        return plain_text

def valid_padding(plain_text, block_size):
    last_chr = plain_text[-1]
    if ord(last_chr) < block_size:
        t_list = list(plain_text)
        c = 0
        while c<ord(last_chr):
            if ord(t_list[-1])!=ord(last_chr):
                raise Exception('Improper PKCS#7 padding')
            t_list.pop(-1)
            c+=1
        return ''.join(t_list)
    else:
        return plain_text

def cbc_encrypt(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pks_padding(plain_text, BLOCK_SIZE)
    cipher_text = cipher.encrypt(padded_text)
    #return cipher_text.encode('hex')
    return cipher_text

def bitwise_xor(s1,s2):
    return ''.join([chr(ord(x)^ord(y)) for x,y in zip(s1,s2)])

class bank(object):
    def __init__(self):
        self.key = RANDOM_KEY

    def validate_message(self, message):
        MAC = message[-16:]
        iv = message[-32:-16]
        message = message[:-32]
        return cbc_encrypt(message, self.key, iv)[-16:] == MAC

    def validate_transfer_list(self, xfer):
        MAC = xfer[-16:]
        return cbc_mac(xfer[:-16], '\0'*16) == MAC

def cbc_mac(m, iv):
    c = cbc_encrypt(m, RANDOM_KEY, iv)
    return c[-16:]

def create_transfer(from_id, to_id, amount):
    message = "from=#{0}&to=#{1}&amount=#{2}".format(from_id, to_id, amount)
    iv = urandom(BLOCK_SIZE)
    MAC = cbc_mac(message, iv)
    return message + iv + MAC

def create_transfer_list(from_id, to_list, amount_list):
    message = "from=#{}&tx_list=#".format(from_id)
    transactions = ";".join([str(to) + ":" + str(amt) for to, amt in zip(to_list, amount_list)])
    message += transactions
    iv = '\0' * BLOCK_SIZE
    MAC = cbc_mac(message, iv)
    return message + MAC

def haxxor_transfer_part_one():
    B = bank()
    my_id = 1
    your_id = 2
    amount = 1000000
    m = create_transfer(my_id, my_id, amount)

    iv0 = m[-32:-16]
    first_block = m[:16]
    new_first_block = "from=#2&to=#1&am"
    new_iv = bitwise_xor(iv0, bitwise_xor(first_block, new_first_block))
    new_m = new_first_block + m[16:-32] + new_iv + m[-16:]
    print B.validate_message(new_m)

def haxxor_transfer_part_two():
    B = bank()
    my_id = 1
    to_list = [2,3,4,5, 6, 7]
    amt_list = [100,200,300,400,5,1]
    m0 = create_transfer_list(my_id, to_list, amt_list)
    MAC = m0[-16:]

    extension = ';2:10000000'
    MAC2 = cbc_mac(extension, MAC)
    new_transfer = m0[:-16] + extension + MAC2
    print B.validate_transfer_list(m0)
    print new_transfer
    print B.validate_transfer_list(new_transfer)



if __name__ == "__main__":
    haxxor_transfer_part_one()
    haxxor_transfer_part_two()
