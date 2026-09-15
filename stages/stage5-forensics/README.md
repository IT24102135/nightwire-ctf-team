# Stage 5 - Packet Whisper

**Domain:** Networking / Digital Forensics
**Difficulty:** Moderate-Hard

## Artifacts

| File | Purpose |
|------|---------|
| `artifacts/exfil_capture.pcapng` | DNS-tunnelled TXT queries and FTPS session |
| `artifacts/handoff.txt` | Handoff file transferred over FTPS |
| `sslkeylog.txt` | TLS session keys for FTPS decryption |

## Objective

1. Reconstruct the DNS-tunnelled exfiltration data
2. Extract the passphrase from DNS TXT queries
3. Decrypt the FTPS session using sslkeylog.txt
4. Extract and decrypt handoff.txt to reveal the flag

## Tools

- Wireshark / tshark
- Python 3
- Base64 decoder

## Solution Path

1. Open `exfil_capture.pcapng` in Wireshark
2. Filter DNS TXT queries: `dns.qry.type == 16`
3. Extract subdomain labels in timestamp order
4. Concatenate and base64-decode to obtain the passphrase
5. Load `sslkeylog.txt` in Wireshark (TLS preferences)
6. Follow decrypted FTP-DATA stream to extract handoff.txt
7. Decrypt handoff.txt with the passphrase

## Flag

NIGHTWIRE{packet_trail_complete}

## Validation

- CTFd flag format: `^NIGHTWIRE\{[A-Za-z0-9_]{8,40}\}$`
- SHA-256 server-side comparison
