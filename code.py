import requests
import pandas as pd

# GitHub API URL
url = "https://api.github.com/search/users"

# Set your GitHub token here
token = "my_token"  # Replace with your actual token

# Set query parameters for users in Stockholm with > 100 followers
params = {
    "q": "location:Stockholm followers:>100",
    "per_page": 100,
    "page": 1
}

# Set headers with authentication
headers = {
    "Authorization": f"token {token}"
}

users = []

while True:
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching users: {response.status_code} - {response.text}")
        break

    data = response.json()
    users.extend(data['items'])
    print(f"Fetched {len(data['items'])} users on page {params['page']}.")

    # Check for next page
    if 'next' not in response.links:
        break
    params['page'] += 1

# Create DataFrame and clean the data
user_data = []
for user in users:
    user_data.append({
        "login": user['login'],
        "name": user.get('name', ''),
        "company": user.get('company', '').strip().lstrip('@').upper(),
        "location": user.get('location', ''),
        "email": user.get('email', ''),
        "hireable": user.get('hireable', ''),
        "bio": user.get('bio', ''),
        "public_repos": user.get('public_repos', ''),
        "followers": user.get('followers', ''),
        "following": user.get('following', ''),
        "created_at": user.get('created_at', '')
    })

print(f"Total users fetched: {len(user_data)}")  # Debugging statement to show total users fetched

# Save to CSV
users_df = pd.DataFrame(user_data)
users_df.to_csv('users.csv', index=False)

repositories = []

for user in users_df['login']:
    repo_url = f"https://api.github.com/users/{user}/repos"
    repo_params = {
        "per_page": 500,
        "sort": "pushed"
    }
    
    repo_response = requests.get(repo_url, headers=headers, params=repo_params)
    
    if repo_response.status_code != 200:
        print(f"Error fetching repositories for {user}: {repo_response.status_code} - {repo_response.text}")
        continue  # Skip this user if there's an error

    repo_data = repo_response.json()
    print(f"Fetched {len(repo_data)} repositories for user {user}.")  # Debugging statement for repos count

    for repo in repo_data:
        repositories.append({
            "login": user,
            "full_name": repo['full_name'],
            "created_at": repo['created_at'],
            "stargazers_count": repo['stargazers_count'],
            "watchers_count": repo['watchers_count'],
            "language": repo['language'],
            "has_projects": repo['has_projects'],
            "has_wiki": repo['has_wiki'],
            "license_name": repo['license']['name'] if repo.get('license') else ''
        })

print(f"Total repositories fetched: {len(repositories)}")  # Debugging statement to show total repos fetched

# Save to CSV
repos_df = pd.DataFrame(repositories)
repos_df.to_csv('repositories.csv', index=False)
