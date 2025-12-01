import requests
import json

with open("access_token.txt", "r") as f:
    access_token = f.read()

url = "http://127.0.0.1:8000/api/v1/auth/users/me/"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}"
}

try:
    response = requests.get(url, headers=headers)
    print(response.json())
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
