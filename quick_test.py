import requests
import json

try:
    print("Testing dataset info...")
    response = requests.get("http://localhost:8009/api/dataset-info", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
