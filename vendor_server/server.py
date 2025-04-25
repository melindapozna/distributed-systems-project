from flask import Flask, request

app = Flask(__name__)

items = [10, 120, 3, -10, 413, -1000]
@app.route('/search')
def search():
    query = request.args.get('query')
    return [x for x in items if x < int(query)]

app.run(host='127.0.0.1', port=1642)



