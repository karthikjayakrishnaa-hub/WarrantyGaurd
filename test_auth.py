import requests
import sys

def test_claims():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "email": "admin@warrantyguard.ai",
        "password": "admin123"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Login successful.")
        token = data['access_token']
    except Exception as e:
        print(f"Login failed: {e}")
        if response is not None:
            print(response.text)
        sys.exit(1)

    url_claims = "http://localhost:8000/api/v1/claims/?limit=1"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(url_claims, headers=headers)
        print("Status code:", response.status_code)
        print(response.json())
    except Exception as e:
        print(f"Get claims failed: {e}")
        if response is not None:
            print(response.text)

if __name__ == "__main__":
    test_claims()
