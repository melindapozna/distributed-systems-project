# A server for handling new vendor servers

from flask import Flask, request

server_address = '127.0.0.1'
server_port = 3001

VENDOR_SERVERS = []
app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    address = request.get_json()
    if type(address) != str:
        return "Incorrect body, send address only", 400
    VENDOR_SERVERS.append(address)
    print(VENDOR_SERVERS)
    return "Connected successfully", 200

def start_vendor_handling_server():
    app.run(host=server_address, port=server_port)

if __name__ == '__main__':
    start_vendor_handling_server()