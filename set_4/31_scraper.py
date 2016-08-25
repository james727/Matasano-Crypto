import requests
import time

def get_baseline_time():
    t0 = time.time()
    r = requests.get('http://0.0.0.0:8080/file=foo&signature=bar')
    return time.time()-t0

def guess_and_get_time(filename, signature):
    t0 = time.time()
    r = requests.get('http://0.0.0.0:8080/file='+filename+'&signature='+signature)
    return time.time()-t0, r.text

def pad_guess(guess):
    return guess + (40-len(guess))*'a'

def get_signature(filename):

    known_chars = ''
    last_return = ''
    last_time = get_baseline_time()

    while last_return != '200':
        last_guess = known_chars
        for i in range(48,58) + range(97,104):
            current_char = chr(i)
            current_guess = known_chars + current_char
            time_to_return, last_return = guess_and_get_time(filename, pad_guess(current_guess))
            if last_return == '200':
                return current_guess
            if (time_to_return - last_time) >= .03:
                known_chars = current_guess
                print known_chars
                last_time = time_to_return
                break
            last_time = time_to_return
        if known_chars == last_guess:
            # go back 1
            known_chars = known_chars[:-1]

if __name__ == "__main__":

    filename = 'pwd'
    print get_signature(filename)
