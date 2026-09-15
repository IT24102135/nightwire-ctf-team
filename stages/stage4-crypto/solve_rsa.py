#!/usr/bin/env python3
"""
NIGHTWIRE Stage 4 - RSA Solver
Demonstrates factoring a weak 512-bit RSA modulus.
"""

from pathlib import Path
import sys

try:
    from Crypto.PublicKey import RSA
    from Crypto.Util.number import long_to_bytes, inverse
except ImportError:
    print("[!] pycryptodome required: pip install pycryptodome")
    sys.exit(1)


PUBKEY_PATH = "pubkey.pem"
CIPHERTEXT_PATH = "service_creds.enc"


def load_pubkey():
    with open(PUBKEY_PATH, "rb") as f:
        return RSA.import_key(f.read())


def factor_weak_modulus(n):
    """
    Factor a small RSA modulus using trial division for demonstration.
    For a real 512-bit key, use RsaCtfTool or FactorDB.
    """
    print(f"[*] Factoring modulus n = {n}")
    for p in range(2, 10_000_000):
        if n % p == 0:
            q = n // p
            print(f"[+] Found factor p = {p}")
            print(f"[+] Found factor q = {q}")
            return p, q
    raise ValueError("No factor found in range")


def decrypt(ciphertext, p, q, e):
    n = p * q
    phi = (p - 1) * (q - 1)
    d = inverse(e, phi)
    plaintext = pow(ciphertext, d, n)
    return long_to_bytes(plaintext)


def main():
    key = load_pubkey()
    n = key.n
    e = key.e
    print(f"[*] Loaded public key: n = {n}, e = {e}")

    with open(CIPHERTEXT_PATH, "rb") as f:
        ciphertext = int.from_bytes(f.read(), "big")

    p, q = factor_weak_modulus(n)
    plaintext = decrypt(ciphertext, p, q, e)
    print("[+] Decrypted credentials:")
    print(plaintext.decode(errors="replace"))


if __name__ == "__main__":
    main()
