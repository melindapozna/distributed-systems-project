from client import Client
from rich.console import Console
from rich.table import Table


def main_menu():
    print('''1. Search
2. List all books
0.Exit''')
    return int(input('Your choice:'))


def buy_menu(books, client):
    try:
        book_no = int(input('Enter the Serial Number of the book you want to purchase (Back = 0):'))
        if book_no > len(books):
            raise ValueError
        elif book_no == 0:
            main_menu()
        else:
            client.buy(books[i - 1])
    except ValueError:
        print('Invalid choice')


if __name__ == '__main__':
    print("Book Store")
    client = Client()
    console = Console()
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
                # styling doesn't show in PyCharm terminal!
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
                buy_menu(search_result, client)
            elif choice == 2:
                print('Available books:')
                all_books = client.search('')

        except ValueError:
            print('Invalid choice')
            main_menu()
