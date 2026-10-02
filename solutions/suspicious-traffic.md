# Solution: Suspicious Traffic

## Objective
Reconstruct HTTP beacon payload from packet capture.

## Steps
1. Open `suspicious_traffic.pcap` in Wireshark.
2. Apply display filter: `http`.
3. Right-click the HTTP POST packet and select **Follow -> TCP Stream**.
4. The request body contains:
   `client_id=wkstn_45&status=sync&data=CTF{pcap_fl0w_analyz3d_4421}`
5. Submit `CTF{pcap_fl0w_analyz3d_4421}`.
