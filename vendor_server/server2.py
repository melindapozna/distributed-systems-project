from flask import Flask, request, jsonify
from dotenv import load_dotenv, set_key
from os import getenv


from database import Database
from register_server import register_server


server_address = '127.0.0.1'
server_port = 1643

# Registering the vendor server with the hub upon first launch
load_dotenv(dotenv_path='.env2')
if not getenv('SERVER_REGISTERED'):
    result = register_server(server_address, server_port)
    if not result:
        print('Failed to register the vendor server')
        exit(0)
    print('Successfully registered the vendor server')
    set_key('.env2', 'SERVER_REGISTERED', '1')

# Database setup
db_address = '127.0.0.1'
db_port = 27017
db_name = "Products2"
db = Database(db_address, db_port, db_name, allow_transactions=False)


app = Flask(__name__)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    try:
        search_results = db.search('Books', query, ['name'])
        return jsonify(
            [{
                'id': str(x['_id']),
                'name': x['name'],
                'price': x['price'],
                'quantity': x['quantity']
            } for x in search_results]
        )
    except Exception as e:
        print(f'Error during search: {e}')
        return jsonify({'error': 'Error during search'}), 500

@app.route('/buy', methods=['POST'])
def buy():
    body = request.get_json()
    if type(body) is not list:
        return jsonify({'error': 'Malformed request body'}), 400

    result = db.remove_items('Books', body)
    if result is None:
        return jsonify({'error': 'Malformed request body'}), 400

    price, updated_items = result
    if price == -1:
        return jsonify({'error': 'Not enough items in stock'}), 409
    return jsonify({'price': price, 'items': updated_items}), 200

if __name__ == '__main__':
    app.run(host=server_address, port=server_port)
