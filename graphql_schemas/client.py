import requests

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

def execute_graphql(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post(GRAPHQL_ENDPOINT, json={"query": query}, headers=headers)
    return response.json()
