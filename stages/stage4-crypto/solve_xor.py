from pathlib import Path

KEY = b"NWKEY"

ciphertext = Path("config_backup.enc").read_bytes()

plaintext = bytes(
    byte ^ KEY[i % len(KEY)]
    for i, byte in enumerate(ciphertext)
)

print(plaintext.decode())
