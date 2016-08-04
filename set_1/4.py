import urllib2

def evaluate_string(s):
    c = 0
    for char in s:
        if char in "etaoinETAOIN":
            c+=1
    return c

def decode_string(s):
    max_score = 0
    max_string = ""
    max_key = ""
    for i in range(1,255):
        n = "".join(map(lambda x: chr(ord(x)^i), s.decode('hex')))
        if evaluate_string(n) > max_score:
            max_score = evaluate_string(n)
            max_string = n
            max_key = chr(i)
    return max_string, max_key

max_score = 0
max_string = 0

for line in urllib2.urlopen('http://cryptopals.com/static/challenge-data/4.txt'):
    s = line.strip()
    decoded_string = decode_string(s)
    if evaluate_string(decoded_string)>max_score:
        max_score = evaluate_string(decoded_string)
        max_string = decoded_string

print max_string
