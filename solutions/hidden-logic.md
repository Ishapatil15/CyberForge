# Solution: Hidden Logic

## Objective
Invert the serial calculation algorithm: `transformed = (ord(ch) ^ 0x37) + i * 3`.

## Solver Script
```python
targets = [116, 116, 32, 23, 15, 21, 33]
serial = "".join([chr((t - i * 3) ^ 0x37) for i, t in enumerate(targets)])
print("Calculated serial:", serial)  # CF-9418
```

## Running
```bash
python validator.py CF-9418
```
Output:
`[+] License Validated! Registered Flag: CTF{v4l1dat10n_l0g1c_d3c0d3d_941}`
