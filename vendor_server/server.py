from flask import Flask, request, jsonify

from vendor_server.database import Database

server_address = '127.0.0.1'
server_port = 1642

db_address = '127.0.0.1'
db_port = 27017
db_name = "Products"
db = Database(db_address, db_port, db_name)

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
    if 'id' not in body:
        return jsonify({'error': 'No id in request body'}), 400
    id = body['id']
    try:
        price = db.remove_one('Books', id)
        if price is None:
            return jsonify({'error': 'Not enough items in stock'}), 400 # TODO change status code
        return jsonify(price)
    except KeyError as _:
        return jsonify({'error': f'Object with this id does not exist'}), 404
    except Exception as e:
        return jsonify({'error': f'Error during buying: {e}'}), 500

if __name__ == '__main__':
    app.run(host=server_address, port=server_port)
