# This file deletes the database contents and fills it with example values

from server import db
from server2 import db as db2


db.drop_collection('Books')
books = [('Silly Book', 10, 100), ('Medium Book', 30, 1), ('Smart Book', 50, 0)]
db.insert('Books', [{'name': n, 'price': p, 'quantity': q} for n, p, q in books])


db2.drop_collection('Books')
books = [('Silly Book 2', 10, 20), ('Medium Book 2', 30, 15), ('Smart Book 2', 50, 1    )]
db2.insert('Books', [{'name': n, 'price': p, 'quantity': q} for n, p, q in books])
