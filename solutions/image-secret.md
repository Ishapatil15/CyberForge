# Solution: Image Secret

## Objective
Extract hidden text from PNG chunk and trailing data.

## Steps
1. Download `cyber_artifact.png`.
2. Run strings:
   ```bash
   strings cyber_artifact.png | grep "CTF{"
   ```
3. Output:
   `Flag: CTF{st3g0_png_chUnk_unc0v3r3d_215}`
4. Submit `CTF{st3g0_png_chUnk_unc0v3r3d_215}`.
