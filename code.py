import os
import requests

token = os.getenv("GITHUB_TOKEN")

# Define headers with the token for authentication
headers = {"Authorization": f"token {token}"}

# Make the API call
url = "https://api.github.com/search/users?q=location:Stockholm+followers:>100"
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    print(data)  # Process data as needed
else:
    print(f"Failed to retrieve data: {response.status_code} - {response.text}")
