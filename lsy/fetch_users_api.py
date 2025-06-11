import requests
response = requests.get("https://jsonplaceholder.typicode.com/users")
users = response.json()
for user in users:
    print(user['name'], "-", user['email'])
