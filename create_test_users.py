import requests

URL = "http://localhost:8000/users/"

for i in range(1, 11):
    response = requests.post(URL, json={
        "name": f"Test User {i}",
        "email": f"testuser{i}@example.com"
    })
    print(i, response.status_code, response.json())