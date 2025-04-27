import xmlrpc.client


class Client:
    def __init__(self):
        self.server = xmlrpc.client.ServerProxy('http://localhost:3000')

    # searches books by substring in their title
    def search(self, book_title):
        self.server.search()
        # todo parse xml
        # populate books with real data
        books = [
            {
                'title': 'Example book',
                'price': 10,
                'amount': 2
            }
        ]

        def books_exist(book):
            return book['amount'] != 0

        return list(filter(books_exist, books))

    def buy(self, book):
        xml_book = ""
        self.server.buy(xml_book)
