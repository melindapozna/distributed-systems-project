import http.client
import json

connection = http.client.HTTPConnection("127.0.0.1:1642")
connection.request("GET", "/search?query=silly")
response = connection.getresponse()
response_body = json.loads(response.read().decode())
print(response.status)
print(response_body)
id = response_body[0]['id']

headers = {'Content-type': 'application/json'}
request_body = json.dumps({'id': id})
connection.request("POST", "/buy", request_body, headers)
response = connection.getresponse()
print(response.status)
print(response.read().decode())

connection.close()
