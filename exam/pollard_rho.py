import sys
import math

def gcd(x, y):
   while(y):
       x, y = y, x % y

   return x

def g(n, mod):
    return (n*n + 1) % mod

def pollard_rho(num):
    x = 2
    y = 2
    d = 1

    while d == 1:
        x = g(x, num)
        y = g(g(y, num), num)
        d = gcd(int(math.fabs(x-y)), num)

    if d == num:
        return "NO FACTORS"
    else:
        return str(d)


num = int(sys.argv[1])
print "Factors of", num

factors = []
result = pollard_rho(num)
while(result != "NO FACTORS"):
    factors.append(result)
    num = num // int(result)
    result = pollard_rho(num)


if len(factors) == 0:
    print result
else:
    factors.append(num)
    for i in factors:
        print i
