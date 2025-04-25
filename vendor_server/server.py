from flask import Flask, request

from vendor_server.database import Database

server_address = '127.0.0.1'
server_port = 1642

db_address = '127.0.0.1'
db_port = 27017
db_name = "Products"
db = Database(db_address, db_port, db_name)

'''book_names = ['Silly Book', 'Medium Book', 'Smart Book']
book_prices = [10, 30, 50]
db.insert('Books',
          [{'name': n, 'price': p} for n, p in zip(book_names, book_prices)])'''
app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query')
    search_results = db.search('Books', query, ['name'])
    return [x['name'] for x in search_results]

app.run(host=server_address, port=server_port)



