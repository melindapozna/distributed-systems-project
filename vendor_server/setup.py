# This file deletes the database contents and fills it with example values

from vendor_server.server import db


db.drop_collection('Books')
books = [('Silly Book', 10, 100), ('Medium Book', 30, 1), ('Smart Book', 50, 0)]
db.insert('Books', [{'name': n, 'price': p, 'quantity': q} for n, p, q in books])
