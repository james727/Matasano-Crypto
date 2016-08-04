text = """Burning 'em, if you ain't quick and nimble
I go crazy when I hear a cymbal"""
key = "ICE"

def repeating_encrypt(text,key):
    new_string = ""
    key = key * (len(text) // len(key)+1)
    return "".join([chr(ord(x)^ord(y)) for x,y in zip(text, key)])

def repeating_decrypt(text,key):
    new_string = ""
    key = key * (len(text) // len(key)+1)
    return "".join([chr(ord(x)^ord(y)) for x,y in zip(text, key)])

encoded_string = bytes(repeating_encrypt(text,key)).encode('hex')
check_string = """0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a26226324272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b20283165286326302e27282f"""
print str(encoded_string) == check_string
print repeating_decrypt(encoded_string.decode('hex'), key)
