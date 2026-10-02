# Solution: Strange File

## Objective
Repair the corrupted ZIP magic bytes from `XX\x03\x04` back to `PK\x03\x04`.

## Steps
1. Inspect `mystery.bin` in a hex editor:
   First 4 bytes are `58 58 03 04`.
2. Notice the presence of file names like `secret_recovery.txt` in the archive directory.
3. Repair the first two bytes to `50 4B` (`PK`).
   Python one-liner:
   ```python
   data = bytearray(open("mystery.bin", "rb").read())
   data[0], data[1] = 0x50, 0x4B
   open("repaired.zip", "wb").write(data)
   ```
4. Extract `repaired.zip` and read `secret_recovery.txt`:
   `Recovered Flag: CTF{p0lygl0t_m4g1c_byt3s_f1x3d_608}`
5. Submit `CTF{p0lygl0t_m4g1c_byt3s_f1x3d_608}`.
