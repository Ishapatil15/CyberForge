# Solution: Memory Clue

## Objective
Extract the secret vault token from process memory.

## Steps
1. Download `memory_minidump.raw`.
2. Run strings to search for environment keys:
   ```bash
   strings memory_minidump.raw | grep -i "CYBERFORGE"
   ```
3. Output:
   `CYBERFORGE_VAULT_TOKEN=CTF{m3m0ry_str1ngs_unv31l_993}`
4. Submit `CTF{m3m0ry_str1ngs_unv31l_993}`.
