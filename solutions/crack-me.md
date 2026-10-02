# Solution: Crack Me

## Objective
Reverse engineer the XOR obfuscation to find the passkey and unlock the flag.

## Steps
1. Unzip `crackme.zip`.
2. Inspect `crackme.py`. The passkey check compares `candidate ^ 0x5A` to `SECRET_XOR`.
3. Recover the key:
   ```python
   secret_xor = bytes([x ^ 0x5A for x in b"CyberForgeKey42"])
   key = bytes([b ^ 0x5A for b in secret_xor]).decode()
   print("Key:", key)  # CyberForgeKey42
   ```
4. Run:
   ```bash
   python crackme.py CyberForgeKey42
   ```
5. Output: `[+] Access Granted! Flag: CTF{str1ngs_and_x0r_r3v3rs1ng_619}`.
