import random

for i in range(10000):
    x = random.randint(1, 2**20)
    y = 2**random.randint(1, 19)
    assert x%y == x & y-1
