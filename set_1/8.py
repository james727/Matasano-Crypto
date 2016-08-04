import urllib2

def get_file_list(filename):
    contents = ""
    for line in urllib2.urlopen(filename):
        s = line#.rstrip('\n')
        contents+=s
    return contents.split()

def get_chunks(text):
    chunks = []
    for i in range(20):
        chunk = text[0+16*i:16+16*i]
        chunks.append(chunk)
    return chunks

def chunk_frequency_dictionary(chunks):
    freq_dict = {}
    for chunk in chunks:
        try:
            freq_dict[chunk]+=1
        except:
            freq_dict[chunk]=1
    return freq_dict

def ecb_score(freq_dict):
    return 1.0/len(freq_dict.keys())


def main():
    filename = "http://cryptopals.com/static/challenge-data/8.txt"
    s = get_file_list(filename)
    for text in s:
        chunks = get_chunks(text)
        freq_dict = chunk_frequency_dictionary(chunks)
        score = ecb_score(freq_dict)
        print score

main()
