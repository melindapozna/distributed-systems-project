import http.client
import json

hub_address = '127.0.0.1'
hub_port = 3001

def register_server(server_address: str, server_port: int) -> bool:
    connection = http.client.HTTPConnection(f'{hub_address}:{hub_port}')
    headers = {'Content-type': 'application/json'}
    payload = f'http://{server_address}:{server_port}'
    request_body = json.dumps(payload)
    connection.request('POST', '/register', request_body, headers)
    response = connection.getresponse()
    connection.close()
    return response.status == http.HTTPStatus.OK
