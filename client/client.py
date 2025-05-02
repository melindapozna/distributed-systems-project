import xmlrpc.client
import xml.etree.ElementTree as ET


class Client:
    def __init__(self):
        self.server = xmlrpc.client.ServerProxy('http://localhost:3000')

    # searches books by substring in their title
    def search(self, book_title):
        #self.server.search()
        # todo parse xml
        # populate books with real data
        books = [
            {
                'title': 'Example book',
                'price': 10,
                'amount': 2
            },
            {
                'title': 'Another book',
                'price': 40,
                'amount': 3
            }
        ]

        def books_exist(book):
            return book['amount'] != 0

        return list(filter(books_exist, books))

    def buy(self, books):
        root = ET.Element("root")
        for book in books:
            print(book)
            xml_book = ET.SubElement(root, 'book')
            ET.SubElement(xml_book, 'title').text = book['title']
            # todo: do we want individual or total price?
            ET.SubElement(xml_book, 'price').text = book['individual_price']
            ET.SubElement(xml_book, 'amount').text = book['amount']
        tree = ET.ElementTree(root)

        #self.server.buy(tree)
