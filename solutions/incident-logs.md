# Solution: Incident Logs

## Objective
Correlate logs to find attacker IP and decode the executed command payload.

## Steps
1. Unzip `incident_logs.zip`.
2. Inspect `auth.log`: `203.0.113.88` successfully logged in as `svc-deploy`.
3. In `server.log`: `203.0.113.88` called `POST /admin/tools/runner`.
4. In `application.log`:
   `echo Q1RGe2wwZ19jMHJyM2xhdDEwbl9kM3QzY3QzZF81MTJ9 | base64 -d`
5. Decode `Q1RGe2wwZ19jMHJyM2xhdDEwbl9kM3QzY3QzZF81MTJ9`:
   ```bash
   echo "Q1RGe2wwZ19jMHJyM2xhdDEwbl9kM3QzY3QzZF81MTJ9" | base64 -d
   ```
6. Output: `CTF{l0g_c0rr3lat10n_d3t3ct3d_512}`.
