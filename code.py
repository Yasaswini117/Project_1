import requests
import pandas as pd

# GitHub API URLs
search_url = "https://api.github.com/search/users"
user_url = "https://api.github.com/users/"

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
    response = requests.get(search_url, headers=headers, params=params)
    
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
    # Fetch additional user details
    user_response = requests.get(user_url + user['login'], headers=headers)
    
    if user_response.status_code != 200:
        print(f"Error fetching details for user {user['login']}: {user_response.status_code} - {user_response.text}")
        continue
    
    user_details = user_response.json()
    
    # Handle potential None values for company, location, name, email, and hireable
    company = user_details.get('company')
    location = user_details.get('location')
    name = user_details.get('name', '')  # This will return '' if name is None
    email = user_details.get('email', '')  # Email may be missing
    hireable = user_details.get('hireable', '')  # Hireable may be missing

    user_data.append({
        "login": user['login'],
        "name": name.strip() if name else '',  # Cleaned name
        "company": company.strip().lstrip('@').upper() if company else '',  # Cleaned company name
        "location": location.strip() if location else '',  # Cleaned location
        "email": email,  # Email value
        "hireable": hireable,  # Hireable value
        "bio": user_details.get('bio', ''),  # Bio may be missing
        "public_repos": user_details.get('public_repos', 0),  # Default to 0 if not available
        "followers": user_details.get('followers', 0),        # Default to 0 if not available
        "following": user_details.get('following', 0),        # Default to 0 if not available
        "created_at": user_details.get('created_at', '')
    })

print(f"Total users fetched: {len(user_data)}")  # Debugging statement to show total users fetched

# Create DataFrame
users_df = pd.DataFrame(user_data)

# Check for missing values
missing_values = users_df.isnull().sum()
print("Missing values in the DataFrame:\n", missing_values)

# Count how many fields are missing
missing_company_count = users_df['company'].isnull().sum()
missing_email_count = users_df['email'].isnull().sum()
missing_hireable_count = users_df['hireable'].isnull().sum()
missing_name_count = users_df['name'].isnull().sum()

print(f"Number of users with missing names: {missing_name_count}")
print(f"Number of users with missing companies: {missing_company_count}")
print(f"Number of users with missing email addresses: {missing_email_count}")
print(f"Number of users with missing hireable status: {missing_hireable_count}")

# Print the DataFrame to check values
print(users_df.head())  # Debugging statement to check first few rows of DataFrame

# Save cleaned user data to CSV
users_df.to_csv('users.csv', index=False)
print(f"User data saved to users.csv with {len(users_df)} records.")

repositories = []

for user in users_df['login']:
    repo_url = f"https://api.github.com/users/{user}/repos"
    repo_params = {
        "per_page": 500,
        "sort": "pushed"
    }
    
    repo_response = requests.get(repo_url, headers=headers)
    
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

# Save repository data to CSV
repos_df = pd.DataFrame(repositories)
repos_df.to_csv('repositories.csv', index=False)
print(f"Repository data saved to repositories.csv with {len(repos_df)} records.")
