# Solution: The Forgotten Document

## Objective
Trace the decommissioned asset tag to its escrow notes.

## Steps
1. Unzip `audit_records.zip`.
2. `decommission_memo.txt` directs to `legacy-backup.internal`.
3. In `dns_zone.txt`, `legacy-backup.internal` is a CNAME for `asset-9941.storage.internal`.
4. In `server_inventory.csv`, search for `asset-9941`.
5. The `escrow_notes` field reads:
   `Decommission recovery key: CTF{d0cum3nt_arch1v3_unh1dd3n_782}`
6. Submit `CTF{d0cum3nt_arch1v3_unh1dd3n_782}`.
