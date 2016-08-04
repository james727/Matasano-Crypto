import urllib2

def hamming_distance(s1,s2):
    s1_s2_xor = ''.join([bin(ord(s11)^ord(s22)) for s11, s22 in zip(s1,s2)])
    return s1_s2_xor.count('1')

def normalized_distance(text, keysize):
    first_chunk = text[:keysize]
    second_chunk = text[keysize:2*keysize]
    third_chunk = text[2*keysize:3*keysize]
    fourth_chunk = text[3*keysize:4*keysize]
    dist1 = hamming_distance(first_chunk, second_chunk)/(keysize+0.0)
    dist2 = hamming_distance(second_chunk, third_chunk)/(keysize+0.0)
    dist3 = hamming_distance(third_chunk, fourth_chunk)/(keysize+0.0)
    return (dist1+dist2+dist3)/3

def get_distances(text,key_min,key_max):
    distances = {}
    for key in range(key_min, key_max+1):
        distances[key] = normalized_distance(text, key)
    return distances

def get_short_list_of_keys(text, key_min, key_max):
    distances = get_distances(text, key_min, key_max)
    sorted_keys = sorted(distances, key = distances.get)
    return sorted_keys[:3]

def break_up_ciphertext(text, key_size):
    # return map(''.join, zip(*[iter(text)]*key_size)) WTF
    chunks = []
    for i in range(len(text)//key_size):
        chunks.append(text[0:key_size])
        text = text[key_size:]
    return chunks

def transpose_chunks(chunks):
    return map(''.join, zip(*chunks))

def get_frequencies(s):
    s = s.upper()
    frequencies = {}
    for char in s:
        try:
            frequencies[char]+=1
        except:
            frequencies[char]=1
    return frequencies

def evaluate_string(s):
    frequencies_observed = get_frequencies(s)
    frequency_dict = {' ': 20.0, 'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07}
    c = 0
    n = 0
    for char in frequency_dict:
        try:
            observed = frequencies_observed[char]
        except:
            observed = 0
        expected = (frequency_dict[char]/100)*len(s)
        delta = expected-observed
        c+= (delta**2)
        n+= expected**2
    return c/n

def decode_string(s):
    min_score = 99999999999999999999999
    min_string = ""
    min_key = ""
    #for i in range(65,91)+range(97,123):
    for i in range(1,255):
        n = "".join(map(lambda x: chr(ord(x)^i), s))
        if evaluate_string(n) < min_score:
            min_score = evaluate_string(n)
            min_string = n
            min_key = chr(i)
    return min_key

def get_file_string(filename):
    contents = ""
    for line in urllib2.urlopen(filename):
        s = line.rstrip('\n')
        contents+=s
    return contents

def repeating_encrypt(text,key):
    new_string = ""
    key = key * (len(text) // len(key)+1)
    return "".join([chr(ord(x)^ord(y)) for x,y in zip(text, key)])

def main():
    filename = "http://cryptopals.com/static/challenge-data/6.txt"
    s = get_file_string(filename)
    s = s.decode('base64')
    min_key_length = 2
    max_key_length = 40
    potential_key_lengths = get_short_list_of_keys(s, min_key_length, max_key_length)
    potential_keys = []

    for key_length in potential_key_lengths:
        s_chunks = break_up_ciphertext(s, key_length)
        s_chunks_transposed = transpose_chunks(s_chunks)
        key = ""
        for chunk in s_chunks_transposed:
            key+=decode_string(chunk)
        potential_keys.append(key)

    min_score = 99999999999999999
    min_string = ""
    min_key = ""
    print potential_keys
    for key in potential_keys:
        decrypted_text = repeating_encrypt(s, key)
        score = evaluate_string(decrypted_text)
        if score < min_score:
            min_score = score
            min_string = decrypted_text
            min_key = key
    print repeating_encrypt(s, min_key)
    print
    print min_key


main()
