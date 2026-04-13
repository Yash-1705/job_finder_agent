import requests

def get_github_projects(username):
    url = f"https://api.github.com/users/{username}/repos"
    
    response = requests.get(url)
    repos = response.json()
    projects = []
    for repo in repos:
        projects.append({"name": repo["name"], "description": repo["description"],"language": repo["language"],"url": repo["html_url"]})
    
    return projects