from bson import ObjectId
from flask import Flask, request, jsonify

from vendor_server.database import Database

server_address = '127.0.0.1'
server_port = 1642

db_address = '127.0.0.1'
db_port = 27017
db_name = "Products"
db = Database(db_address, db_port, db_name)

# Switch to False for initial setup
inserted = True
if not inserted:
    books = [('Silly Book', 10, 100), ('Medium Book', 30, 1), ('Smart Book', 50, 0)]
    db.insert('Books',
              [{'name': n, 'price': p, 'quantity': q} for n, p, q in books])

app = Flask(__name__)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    search_results = db.search('Books', query, ['name'])
    return jsonify(
        [{
            'id': str(x['_id']),
            'name': x['name'],
            'price': x['price'],
            'quantity': x['quantity']
        } for x in search_results]
    )


@app.route('/buy', methods=['GET'])
@app.route('/buy', methods=['POST'])
def buy():
    body = request.get_json()
    id = body['id']
    price = db.remove_one('Books', id)
    return jsonify(price)

app.run(host=server_address, port=server_port)
