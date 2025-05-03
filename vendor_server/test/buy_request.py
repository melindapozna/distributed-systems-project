import http.client
import json

connection = http.client.HTTPConnection('127.0.0.1:1642')

def get_id(query: str):
    connection.request('GET', f'/search?query={query}')
    response = connection.getresponse()
    response_body = json.loads(response.read().decode())
    print(response.status)
    print(response_body)
    return response_body[0]['id']

silly_id = get_id('silly')
medium_id = get_id('medium')

headers = {'Content-type': 'application/json'}
payload = [{'id': silly_id, 'quantity': 2},{'id': medium_id, 'quantity': 1}]
request_body = json.dumps(payload)
connection.request('POST', '/buy', request_body, headers)
response = connection.getresponse()
print(response.status)
print(response.read().decode())

connection.close()
