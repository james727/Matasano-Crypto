def pks_padding(plain_text, block_size):
    final_block_length = len(plain_text)%block_size
    padding_needed = block_size-final_block_length
    hex_escape = "\\x{:02x}".format(padding_needed)
    return plain_text+hex_escape*padding_needed

if __name__ == "__main__":
    plain_text = "YELLOW SUBMARINE"
    block_size = 20
    print pks_padding(plain_text, block_size)
