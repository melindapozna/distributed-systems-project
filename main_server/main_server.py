import xmlrpc.server
from socketserver import ThreadingMixIn
from flask import Flask, request
import requests
from collections import defaultdict
import threading

MAIN_SERVER_HOST = 'localhost'
MAIN_SERVER_PORT = 3000
VENDOR_SERVERS = []

class SimpleThreadedXMLRPCServer(ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    pass

class MainServer:

    def search(self, query: str):
        all_results = []
        print(f"Received search request from client for query: '{query}'")
        print(VENDOR_SERVERS)
        for vendor_url in VENDOR_SERVERS:
            search_url = f"{vendor_url}/search"
            print(vendor_url)
            try:
                response = requests.get(search_url, params={'query': query})
                response.raise_for_status()

                vendor_results = response.json()
                print(f"Received {len(vendor_results)} results from {vendor_url}")

                for item in vendor_results:
                    if all(k in item for k in ['id', 'name', 'price', 'quantity']):
                        item_data = {
                            'id': item['id'],
                            'vendor_url': vendor_url,  # store which vendor this item came from
                            'name': item['name'],
                            'price': item['price'],
                            'quantity': item['quantity']
                        }
                        all_results.append(item_data)
                    else:
                        print(f"Skipping malformed item from {vendor_url}: {item}")


            except requests.exceptions.ConnectionError as e:
                print(f"Connection error contacting vendor server {vendor_url}: {e}")
                continue
            except requests.exceptions.Timeout as e:
                print(f"Timeout contacting vendor server {vendor_url}: {e}")
                continue
            except Exception as e:
                # catch-all
                print(f"An unexpected error occurred processing results from {vendor_url}: {e}")
                continue

        print(f"Returned {len(all_results)} total search results to send to client.")
        return all_results

    def buy(self, cart_items: list):
        purchase_results = []
        print(f"Received buy request from client for {len(cart_items)} unique item types in cart.")

        # Group items by vendor
        items_by_vendor = defaultdict(list)
        for item in cart_items:
            # using get to deal with any malformed dicts
            item_id = item.get('id')
            vendor_url = item.get('vendor_url')
            amount_requested = item.get('amount', 0)
            title = item.get('title', 'Unknown Title')
            print(vendor_url)
            print(amount_requested)
            if not vendor_url or amount_requested <= 0:
                print(f"Skipping invalid cart item data: {item}")
                continue
            items_by_vendor[vendor_url].append({'id': item_id, 'quantity': amount_requested})

        total_price_paid = 0
        purchased_items = []
        for vendor_url, item_list in items_by_vendor.items():
            buy_url = f"{vendor_url}/buy"
            headers = {'Content-type': 'application/json'}
            request_body = item_list

            items_printable = ', '.join([f'{item["quantity"]} of {item["id"]}' for item in item_list])
            print(f"Processing buy request for {items_printable} from vendor {vendor_url}")

            try:
                response = requests.post(buy_url, json=request_body, headers=headers)
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        price = response_data['price']
                        # Items from this vendor
                        items_received = response_data['items']
                        if not isinstance(price, (int, float)):
                            print(f"Vendor server {vendor_url} returned non-numeric price for {item_id}: {price}")
                            price = 0
                    except (ValueError, TypeError):
                        print(
                            f"Could not parse price from vendor server {vendor_url} for {item_id}. Response: {response.json().get('error')}")
                        price = 0

                    total_price_paid += price
                    items_printable = ', '.join([f'{item["quantity"]} of {item["name"]}' for item in items_received])
                    print(f"Successfully purchased {items_printable} from {vendor_url}")
                    purchased_items += items_received

                elif response.status_code == 400:
                    print(
                        f"Vendor {vendor_url} reported 400, incorrect request.")
                    continue

                else:
                    # some other http errors, catch-all
                    print(
                        f"Vendor server {vendor_url} returned unexpected status {response.status_code}. Response: {response.json().get('error')}")
                    break  # also stop

            except requests.exceptions.ConnectionError as e:
                print(f"Connection error buying {item_id} from {vendor_url}: {e}")
                break
            except requests.exceptions.Timeout as e:
                print(f"Timeout buying {item_id} from {vendor_url}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error during buy attempt for {item_id}: {e}")
                break

        print("Finished processing all items in the buy request.")
        # xml-rpc does the conversion itself
        return {'price': total_price_paid, 'items': purchased_items}


def run():
    server = xmlrpc.server.SimpleXMLRPCServer(
        (MAIN_SERVER_HOST, MAIN_SERVER_PORT),
        allow_none=True  # allows functions to return None if needed
    )
    server.register_instance(MainServer())
    server.register_introspection_functions()

    print(f"Main server listening on {MAIN_SERVER_HOST}:{MAIN_SERVER_PORT}")
    print(f"Connected to vendor servers: {', '.join(VENDOR_SERVERS)}")
    print("Press Ctrl+C to exit.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Main server shutting down.")
        exit(0)
    except Exception as e:
        print(f"An unexpected error occurred during server operation: {e}")

#
# Vendor server handling server
#
app = Flask(__name__)
server_address = '127.0.0.1'
server_port = 3001


@app.route('/register', methods=['POST'])
def register():
    address = request.get_json()
    if type(address) != str:
        return "Incorrect body, send address only", 400
    VENDOR_SERVERS.append(address)
    print(VENDOR_SERVERS)
    return "Connected successfully", 200


def start_vendor_handling_server():
    while True:
        app.run(host=server_address, port=server_port)


if __name__ == '__main__':
    main_server_thread = threading.Thread(target=run)
    vendor_handler_thread = threading.Thread(target=start_vendor_handling_server)

    main_server_thread.start()
    vendor_handler_thread.start()
