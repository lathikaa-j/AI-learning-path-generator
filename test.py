import requests

url = "https://eol6sxd21oyexp2.m.pipedream.net"

response = requests.post(url, json={
    "query": "DSA in Java"
})

print(response.text)