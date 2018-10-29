import sys
from random import randint


def miller_rabin(num, k):
    if num == 2:
        return "PRIME"
    if num % 2 == 0:
        return "COMPOSITE"

    s = num-1
    d = 0
    while s % 2 == 0:
        s = s // 2
        d = d + 1

    for i in range(0, k):
        a = randint(2, num-2)
        x = pow(a, s, num)

        if x != 1:
            j = 0
            while x != (num - 1):
                if j == d - 1:
                    return "COMPOSITE"
                else:
                    j = j + 1
                    x = (x**2) % num

    return "PROBABLY PRIME"

num = int(sys.argv[1])
k = int(sys.argv[2])

print "num:", num
print "k:", k

print miller_rabin(num, k)


