from pathlib import Path

KEY = b"NWKEY"

plaintext = Path("config_backup.ini").read_bytes()

ciphertext = bytes(
    byte ^ KEY[i % len(KEY)]
    for i, byte in enumerate(plaintext)
)

Path("config_backup.enc").write_bytes(ciphertext)

print("Created config_backup.enc")
