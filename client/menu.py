from client import Client
from rich.console import Console
from rich.table import Table


def main_menu():
    print('''1. Search
2. List all books
3. Go to checkout
0. Exit''')
    return int(input('Your choice:'))


def pretty_print_search_result(search_result, title):
    table = Table(title=title)
    # styling doesn't show in PyCharm terminal, but for example Windows PowerShell works
    table.add_column("S. No.", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Price", justify="right", style="red")
    table.add_column("Available amount", justify="right", style="green")
    for i in range(len(search_result)):
        print(search_result[i])
        table.add_row(str(i + 1),
                      search_result[i]['name'],
                      str(search_result[i]['price']),
                      str(search_result[i]['quantity']))
    console.print(table)


def pretty_print_cart():
    table = Table(title='Your cart')
    table.add_column("S. No.", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Amount", style="green")
    table.add_column("Price", justify="right", style="red")
    total = 0
    for i in range(len(cart)):
        print(cart[i])
        table.add_row(str(i + 1),
                      cart[i]['title'],
                      str(cart[i]['amount']),
                      str(cart[i]['total_price']))
        total += cart[i]['total_price']
    console.print(table)
    print(f'Total: {total} Euros')


def add_to_cart(books, cart):
    try:
        book_no = int(input('Enter the Serial Number of the book you want to purchase (Back = 0):'))
        if book_no > len(books):
            raise ValueError
        elif book_no == 0:
            return
        else:
            chosen_book = books[book_no - 1]
            available_amount = chosen_book['quantity']
            while True:
                amount = int(input(f'How many do you want to purchase? (Max. {available_amount}):'))
                if amount == 0:
                    break
                elif amount > available_amount:
                    print(f'Error: only {available_amount} books are available!')
                    continue
                elif amount < 0:
                    print('Please enter a positive number.')
                    continue
                else:
                    print(f'{amount} Book(s) added to your shopping cart!')
                    books_to_be_purchased = {
                        'id': chosen_book['id'],
                        'title': chosen_book['name'],
                        'individual_price': chosen_book['price'],
                        'vendor_url': chosen_book['vendor_url'],
                        'total_price': chosen_book['price'] * amount,
                        'amount': amount
                    }
                    cart.append(books_to_be_purchased)
                    break
    except ValueError:
        print('Invalid choice')


def remove_from_cart(cart):
    try:
        book_no = int(input('Enter the Serial Number of the book you want to remove (Back = 0):'))
        if book_no > len(cart):
            raise ValueError
        elif book_no == 0:
            return
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
                table_title = f'Showing results for "{title}"'
                search_result = client.search(title)
                pretty_print_search_result(search_result, table_title)
                try:
                    add_to_cart(search_result, cart)
                except ValueError:
                    continue
            elif choice == 2:
                all_books = client.search('')
                pretty_print_search_result(all_books, "All books:")
                try:
                    add_to_cart(all_books, cart)
                except ValueError:
                    continue
            elif choice == 3:
                pretty_print_cart()
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
