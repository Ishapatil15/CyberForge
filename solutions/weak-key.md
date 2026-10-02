# Solution: Weak Key

## Objective
Factorize the close-prime RSA modulus using Fermat's factorization.

## Python Solver
```python
import math

n = 100000000000000000000000000000000000002600000000000000000000000000000000000016819
e = 65537
c = 46067659330438327263983517399802600548005702163511885855970045094123830458235874

a = math.isqrt(n)
if a * a < n:
    a += 1

while True:
    b2 = a * a - n
    b = math.isqrt(b2)
    if b * b == b2:
        break
    a += 1

p = a - b
q = a + b
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)
flag = m.to_bytes((n.bit_length() + 7) // 8, "big").lstrip(b"\x00").decode()
print("Flag:", flag)
```

## Result
`CTF{sm4ll_pr1m3s_br3ak_rsa_339}`
