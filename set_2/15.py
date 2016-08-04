def pks_unpadding(plain_text, block_size):
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

if __name__ == "__main__":
    s1 = "12345678"+chr(8)*8
    s2 = "ICE ICE BABY"+chr(5)*4
    print pks_unpadding(s1,16)
    print pks_unpadding(s2,16)
