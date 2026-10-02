# Solution: Hidden Header

## Objective
Identify the diagnostic header exposed in the HTTP response artifact.

## Steps
1. Download the challenge artifact `response.txt`.
2. Inspect the HTTP headers:
   ```bash
   grep -i "X-CyberForge" response.txt
   ```
3. Locate the header:
   ```http
   X-CyberForge-Diagnostic-Token: CTF{h3ad3r_1nspect10n_mast3r}
   ```
4. Submit the flag: `CTF{h3ad3r_1nspect10n_mast3r}`.
