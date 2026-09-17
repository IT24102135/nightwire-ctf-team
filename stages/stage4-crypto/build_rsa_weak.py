#!/usr/bin/env python3
"""
NIGHTWIRE Stage 4 - Weak RSA Builder
Generates a deliberately weak 512-bit RSA keypair where the primes
are small enough to factor with trial division.

This key is intentionally insecure. Do NOT use outside the CTF VM.
"""

from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes

# Two small primes — chosen so that p * q ≈ 512 bits
# p is ~24 bits, q is ~488 bits (product ≈ 512 bits)
P = 16777259          # 24-bit prime
Q = 0  # will be generated below to reach ~512-bit n


def find_large_prime(bits):
    """Find a probable prime of the given bit length."""
    from Crypto.Util.number import getPrime
    return getPrime(bits)


def main():
    print("[*] Building weak 512-bit RSA key...")

    # Small prime (easy to factor via trial division)
    p = 16777259  # 24-bit prime

    # Large prime — but only one factor is small, so factoring is still easy
    q = find_large_prime(488)  # 488-bit prime

    n = p * q
    e = 65537
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)

    print(f"[+] n bit length: {n.bit_length()}")
    print(f"[+] p (small factor): {p}")
    print(f"[+] q bit length: {q.bit_length()}")

    # Build the RSA key
    key = RSA.construct((n, e, d, p, q))

    # Save private key (server-side only)
    private_pem = key.export_key()
    Path("private.pem").write_bytes(private_pem)
    print("[+] Wrote private.pem (DO NOT COMMIT)")

    # Save public key (shipped to players)
    public_pem = key.publickey().export_key()
    Path("pubkey.pem").write_bytes(public_pem)
    print("[+] Wrote pubkey.pem")

    # Encrypt a sample credential blob
    credential = b"svc_backup:NIGHTWIRE{weak_rsa_factored}\n"
    m = bytes_to_long(credential)
    c = pow(m, e, n)
    Path("service_creds.enc").write_bytes(long_to_bytes(c))
    print("[+] Wrote service_creds.enc")


if __name__ == "__main__":
    main()
