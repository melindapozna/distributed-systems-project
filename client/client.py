import xmlrpc.client

from typing import cast

class Client:
    def __init__(self):
        self.server = xmlrpc.client.ServerProxy('http://localhost:3000')
        try:
            self.server.system.listMethods()
            print("Client: Connection successful.")
        except ConnectionRefusedError:
            print("Client Error: Connection refused. Is the main server running?")
        except Exception as e:
            print(f"Client Error: An unexpected error occurred during connection check: {e}")

    # searches books by substring in their title
    def search(self, book_title):
        if self.server is None:
                print("Client: Cannot perform search, server is not connected.")
                return [] # return empty list if server is down

        print(f"Client: Sending search query '{book_title}' to server...")
        try:

            books_raw_notype = self.server.search(book_title)
            books_raw = cast(list, books_raw_notype)
            print(f"Client: Received {len(books_raw)} results from server.")

            def books_exist(book):
                    # using get defaults to 0 if dict is malformed
                    return book.get('quantity', 0) > 0

            available_books = list(filter(books_exist, books_raw))
            print(f"Client: {len(available_books)} results are currently available (quantity > 0).")

            return available_books

        except Exception as e:
            print(f"Client Error: An unexpected error occurred during search: {e}")
            return []



    def buy(self, cart_items):
            if self.server is None:
                print("Client: Cannot perform purchase, server is not connected.")
                return [] # Return empty list if server is down

            print(f"Client: Sending {len(cart_items)} item types from cart to server for purchase...")
            try:
                purchase_results_notype = self.server.buy(cart_items)
                purchase_results = cast(dict, purchase_results_notype)
                print("Client: Purchase attempt results received from server:")
                for item in purchase_results['items']:
                    title = item.get('name', 'Unknown Item')
                    quantity = item.get('quantity', 0)
                    print(f"  - '{title}' x{quantity}: purchased.")
                print(f'Total price paid: {purchase_results["price"]} euros')
                return purchase_results

            except xmlrpc.client.Fault as err:
                print(f"Client Fault: A server fault occurred during buy: {err.faultCode}, {err.faultString}")
                return [] # return empty list on error
            except Exception as e:
                print(f"Client Error: An unexpected error occurred during buy: {e}")
                return []
