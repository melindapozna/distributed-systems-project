from flask import Flask, request, jsonify

from vendor_server.database import Database

server_address = '127.0.0.1'
server_port = 1642

db_address = '127.0.0.1'
db_port = 27017
db_name = "Products"
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
        return jsonify({'error': 'Not enough items in stock'}), 409 # TODO change status code?
    return jsonify({'price': price, 'items': updated_items}), 200

if __name__ == '__main__':
    app.run(host=server_address, port=server_port)
