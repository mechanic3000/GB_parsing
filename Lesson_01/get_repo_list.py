import requests
import json

req = requests.get("https://api.github.com/users/mechanic3000/repos")

with open('git_repos_list_v2.json', 'w') as file:
    json.dump(req.json(), file)

print("All are done")
