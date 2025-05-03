import http.client
import json

hub_address = '127.0.0.1'
hub_port = 2025 # TODO change as needed

def register_server(server_address: str, server_port: int) -> bool:
    return True

# TODO remove the stub and rename this
def register_server_actual(server_address: str, server_port: int) -> bool:
    connection = http.client.HTTPConnection(f'{hub_address}:{hub_port}')
    headers = {'Content-type': 'application/json'}
    payload = [{'address': server_address, 'port': server_port}]
    request_body = json.dumps(payload)
    connection.request('POST', '/register', request_body, headers)
    response = connection.getresponse()
    connection.close()
    return response.status == http.HTTPStatus.OK
