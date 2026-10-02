# Solution: Broken Access

## Objective
Identify the BOLA transaction and extract the leaked escrow key.

## Steps
1. Download `audit_traffic.json`.
2. Inspect the entries. Transaction `tx_103` uses `tenant_a` credentials to access `invoices/9999`.
3. The response body contains:
   `"admin_escrow_key": "CTF{b0la_auth_m1sconf1g_7714}"`
4. Submit `CTF{b0la_auth_m1sconf1g_7714}`.
