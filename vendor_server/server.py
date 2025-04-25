from flask import Flask, request

from vendor_server.database import Database

server_address = '127.0.0.1'
server_port = 1642

db_address = '127.0.0.1'
db_port = 27017
db = Database(db_address, db_port)
db.insert('example', 'values',
          [{'value': x} for x in [-1000, 10, 1233, 12, -1, 0, 17, 122]])
app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query')
    values = db.select('example', 'values')
    return [x['value'] for x in values if x['value'] < int(query)]

app.run(host=server_address, port=server_port)



