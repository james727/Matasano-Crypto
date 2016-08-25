import requests
import time

def guess_and_get_time(filename, signature):
    t0 = time.time()
    r = requests.get('http://0.0.0.0:8080/file='+filename+'&signature='+signature)
    return time.time()-t0, r.text

def pad_guess(guess):
    return guess + (40-len(guess))*'A'

def mean(numbers):
    return float(sum(numbers))/len(numbers)

def get_max_time_char(time_dict):
    mean_dict = {key: mean(time_dict[key]) for key in time_dict}
    return sorted(time_dict, key = time_dict.get, reverse = True)[0]

def get_signature(filename):
    known_chars = ''
    last_return = ''
    while last_return != '200':
        last_guess = known_chars
        print known_chars
        time_dict = {}
        for j in range(15): # run 15 iterations
            for i in range(48,58) + range(97,104):
                current_char = chr(i)
                current_guess = known_chars + current_char
                time_to_return, last_return = guess_and_get_time(filename, pad_guess(current_guess))
                try:
                    time_dict[chr(i)].append(time_to_return)
                except:
                    time_dict[chr(i)] = [time_to_return]
                if last_return == '200':
                    return current_guess
        next_char = get_max_time_char(time_dict)
        known_chars+=next_char

if __name__ == "__main__":

    filename = 'pwd'
    print get_signature(filename)
