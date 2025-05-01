from client import Client
from rich.console import Console
from rich.table import Table


def main_menu():
    print('''1. Search
2. List all books
3. Go to checkout
0. Exit''')
    return int(input('Your choice:'))


def add_to_cart(books, cart):
    try:
        book_no = int(input('Enter the Serial Number of the book you want to purchase (Back = 0):'))
        if book_no > len(books):
            raise ValueError
        elif book_no == 0:
            main_menu()
        else:
            print("Book added to your shopping cart!")
            cart.append(books[book_no - 1])
    except ValueError:
        print('Invalid choice')


def remove_from_cart(cart):
    try:
        book_no = int(input('Enter the Serial Number of the book you want to remove (Back = 0):'))
        if book_no > len(cart):
            raise ValueError
        elif book_no == 0:
            main_menu()
        else:
            print("Book removed from cart!")
            cart.pop(book_no - 1)
    except ValueError:
        print('Invalid choice')


if __name__ == '__main__':
    print("Book Store")
    client = Client()
    console = Console()
    cart = []
    while True:
        try:
            choice = main_menu()
            if choice == 0:
                print('Exiting...')
                exit(0)
            elif choice == 1:
                title = input('Search (book title):')
                search_result = client.search(title)
                table = Table(title=f'Showing results for "{title}"')
                # styling doesn't show in PyCharm terminal, but for example Windows PowerShell works
                table.add_column("S. No.", style="cyan", no_wrap=True)
                table.add_column("Title", style="magenta")
                table.add_column("Price", justify="right", style="red")
                table.add_column("Available amount", justify="right", style="green")
                for i in range(len(search_result)):
                    table.add_row(str(i + 1),
                                  search_result[i]['title'],
                                  str(search_result[i]['price']),
                                  str(search_result[i]['amount']))

                console.print(table)
                try:
                    add_to_cart(search_result, cart)
                except ValueError:
                    continue
            elif choice == 2:
                print('Available books:')
                all_books = client.search('')
            elif choice == 3:
                table = Table(title='Your cart')
                table.add_column("S. No.", style="cyan", no_wrap=True)
                table.add_column("Title", style="magenta")
                table.add_column("Price", justify="right", style="red")
                total = 0
                for i in range(len(cart)):
                    table.add_row(str(i + 1),
                                  cart[i]['title'],
                                  str(cart[i]['price']))
                    total += cart[i]['price']
                console.print(table)
                print(f'Total: {total} Euros')

                is_purchase = input("Do you want to purchase these books? (y/n):")
                if is_purchase.lower() == "y":
                    client.buy(cart)
                elif is_purchase.lower() == "n":
                    try:
                        remove_from_cart(cart)
                    except ValueError:
                        continue
                else:
                    raise ValueError

        except ValueError:
            print('Invalid choice')
            continue
