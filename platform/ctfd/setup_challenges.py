#!/usr/bin/env python3
"""
NIGHTWIRE - CTFd bulk challenge setup.

Creates all 6 stages as CTFd challenges via the REST API, so you don't have
to type them into the web UI by hand.

Before running:
1. Bring the stack up: docker compose up -d --build   (run from platform/ctfd)
2. Open http://localhost:8000, finish the CTFd setup wizard (create the CTF
   and the admin account) if this is a fresh database.
3. Log in as admin -> click your avatar (top right) -> Settings -> Access
   Tokens -> Generate. Paste that token below as API_TOKEN.
4. pip install requests
5. python setup_challenges.py

Safe to re-run: it skips any challenge whose name already exists.
"""

import sys
import requests

BASE_URL = "http://localhost:8000"
API_TOKEN = "PASTE_YOUR_CTFD_ADMIN_TOKEN_HERE"

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
}

CHALLENGES = [
    {
        "name": "Stage 1 - First Contact",
        "category": "OSINT / Reconnaissance",
        "description": (
            "Solace Telecom just launched a new corporate site. See what you can "
            "find lying around that wasn't meant to be public.\n\n"
            "Target: http://localhost:8082"
        ),
        "value": 100,
        "flags": ["NIGHTWIRE{f1rst_c0nt4ct_0s1nt_succ3ss}"],
    },
    {
        "name": "Stage 2 - Hidden in Plain Sight",
        "category": "Steganography",
        "description": (
            "A network diagram was leaked internally. Someone may have hidden "
            "more in it than just a diagram.\n\n"
            "Target: http://localhost:8083"
        ),
        "value": 100,
        "flags": ["NIGHTWIRE{h1dd3n_1n_pl41n_s1ght}"],
    },
    {
        "name": "Stage 3 - Backdoor Portal",
        "category": "Web Security",
        "description": (
            "A support ticket portal takes a ticket ID and looks it up for you. "
            "See if it trusts that input a bit too much.\n\n"
            "Target: http://localhost:8081/search.php?q="
        ),
        "value": 200,
        "flags": ["NIGHTWIRE{b4ckd00r_p0rt4l_sqli_m4st3r}"],
    },
    {
        "name": "Stage 4 - Recovered Backups",
        "category": "Cryptography",
        "description": (
            "Two files were recovered from a compromised backup server: an "
            "XOR-encrypted config backup and an RSA-encrypted credential blob. "
            "Both are crackable if you look closely at how they were built.\n\n"
            "Target: http://localhost:8084"
        ),
        "value": 200,
        # Either the XOR-recovered flag or the RSA-recovered flag is accepted.
        "flags": [
            "NIGHTWIRE{weak_rsa_factored}",
            "NIGHTWIRE{crypto_backup_recovered}",
        ],
    },
    {
        "name": "Stage 5 - Packet Trail",
        "category": "Network Forensics",
        "description": (
            "A packet capture was pulled from a suspicious host. Something was "
            "leaving the network in a way that isn't supposed to carry data.\n\n"
            "Target: http://localhost:8085"
        ),
        "value": 300,
        "flags": ["NIGHTWIRE{packet_trail_complete}"],
    },
    {
        "name": "Stage 6 - Root of Nightwire",
        "category": "Linux Security (Capstone)",
        "description": (
            "You have SSH access to a low-privilege service account on the "
            "final host. Enumerate the box and find your way to root.\n\n"
            "Connect via the VirtualBox VM's IP as instructed in the report."
        ),
        "value": 400,
        "flags": ["NIGHTWIRE{r00t_0f_n1ghtw1r3_c4pst0n3}"],
    },
]


def get_existing_challenge_names():
    r = requests.get(f"{BASE_URL}/api/v1/challenges?view=admin", headers=HEADERS)
    r.raise_for_status()
    return {c["name"] for c in r.json()["data"]}


def create_challenge(chal):
    payload = {
        "name": chal["name"],
        "category": chal["category"],
        "description": chal["description"],
        "value": chal["value"],
        "state": "visible",
        "type": "standard",
    }
    r = requests.post(f"{BASE_URL}/api/v1/challenges", headers=HEADERS, json=payload)
    r.raise_for_status()
    chal_id = r.json()["data"]["id"]

    for flag in chal["flags"]:
        fr = requests.post(
            f"{BASE_URL}/api/v1/flags",
            headers=HEADERS,
            json={"challenge_id": chal_id, "content": flag, "type": "static"},
        )
        fr.raise_for_status()

    return chal_id


def main():
    if API_TOKEN == "PASTE_YOUR_CTFD_ADMIN_TOKEN_HERE":
        print("Edit this file first: paste your CTFd admin API token into API_TOKEN.")
        sys.exit(1)

    try:
        existing = get_existing_challenge_names()
    except requests.exceptions.RequestException as e:
        print(f"Could not reach CTFd at {BASE_URL}: {e}")
        print("Is 'docker compose up -d --build' running, and did you finish the setup wizard?")
        sys.exit(1)

    for chal in CHALLENGES:
        if chal["name"] in existing:
            print(f"SKIP  (already exists): {chal['name']}")
            continue
        chal_id = create_challenge(chal)
        print(f"CREATED  [{chal_id}] {chal['name']}  ({len(chal['flags'])} flag(s), {chal['value']} pts)")

    print("\nDone. Refresh http://localhost:8000/challenges to see them.")


if __name__ == "__main__":
    main()
