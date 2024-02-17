def counter(num):
    i = 0
    for i in range(num):
        yield i

for res in counter(5):
    print(res)