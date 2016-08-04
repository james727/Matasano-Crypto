s = '1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'

"""def evaluate_string(s):
    c = 0
    for char in s:
        #if ord(char) <= 123 and ord(char) >= 65:
        if char in "etaoinshrdlu":
            c+=1
    return c"""

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
        #print char, expected, observed, delta, delta**2, c
    return c/n

def decode_string(s):
    min_score = 99999999999999999999999
    max_string = ""
    for i in range(1,255):
        n = "".join(map(lambda x: chr(ord(x)^i), s.decode('hex')))
        if evaluate_string(n) < min_score:
            min_score = evaluate_string(n)
            min_string = n
    return min_string

print decode_string(s)
#print evaluate_string("66207>y~*y502<y8y)6,7=y6?y;8:67")
#print evaluate_string("Cooking MC's like a pound of bacon")
#print "\n"*5
#print evaluate_string("**.,+b6e),. e$e5*0+!e*#e'$&*+")
#print get_frequencies("**.,+b6e),. e$e5*0+!e*#e'$&*+")
