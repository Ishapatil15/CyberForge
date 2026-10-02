# Solution: Parameter Hunt

## Objective
Uncover an undocumented parameter in the API routes specification.

## Steps
1. Download `api_routes.json`.
2. Search for `debug` or `override`:
   ```bash
   grep -B 2 -A 5 "developer_override" api_routes.json
   ```
3. In `/api/v2/system/debug`, observe the parameter description containing the escrow key:
   `CTF{und0cum3nted_param_leak_892}`
4. Submit `CTF{und0cum3nted_param_leak_892}`.
