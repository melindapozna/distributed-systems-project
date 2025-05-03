import xmlrpc.server
import requests

MAIN_SERVER_HOST = 'localhost'
MAIN_SERVER_PORT = 3000

VENDOR_SERVERS = [
    'http://localhost:1642' # Yes the server list is still hardcoded, sorry will change very soon
]

class MainServer:

    def search(self, query: str):
        all_results = []
        print(f"Received search request from client for query: '{query}'")

        for vendor_url in VENDOR_SERVERS:
            search_url = f"{vendor_url}/search"
            try:
                response = requests.get(search_url, params={'query': query})
                response.raise_for_status()

                vendor_results = response.json()
                print(f"Received {len(vendor_results)} results from {vendor_url}")

                for item in vendor_results:
                    if all(k in item for k in ['id', 'name', 'price', 'quantity']):
                        item_data = {
                            'id': item['id'],
                            'vendor_url': vendor_url, # store which vendor this item came from
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
                purchase_results.append({
                    'title': title,
                    'requested_amount': amount_requested,
                    'total_price_paid': 0,
                    'success': False,
                    'message': 'Invalid item data or amount requested.'
                })
                continue

            print(f"Processing buy request for id {item_id} (title: {title}) from vendor {vendor_url}. Requested amount: {amount_requested}")

            successful_purchases = 0
            failed_message = ""
            total_price_paid = 0

            buy_url = f"{vendor_url}/buy"
            headers = {'Content-type': 'application/json'}
            request_body = {'id': item_id}

            # attempt to buy one at a time
            for attempt in range(amount_requested):
                try:
                    print(f"Attempt {attempt + 1}/{amount_requested} to buy one unit of {item_id} from {vendor_url}")
                    response = requests.post(buy_url, json=request_body, headers=headers)

                    if response.status_code == 200:
                        try:
                            price = response.json()
                            if not isinstance(price, (int, float)):
                                print(f"Vendor server {vendor_url} returned non-numeric price for {item_id}: {price}")
                                price = 0
                        except (ValueError, TypeError):
                             print(f"Could not parse price from vendor server {vendor_url} for {item_id}. Response: {response.text}")
                             price = 0

                        total_price_paid += price
                        successful_purchases += 1
                        print(f"Successfully bought one unit of {item_id} for price {price}. Total bought so far: {successful_purchases}")

                    elif response.status_code == 400:
                         # insufficient stock
                         failed_message = f"Insufficient stock (bought {successful_purchases} out of {amount_requested} requested)."
                         print(f"Vendor {vendor_url} reported 400 for {item_id} after {successful_purchases} successful buys. Response: {response.text}")
                         break # stop trying to buy more of this item

                    elif response.status_code == 404:
                         # item not found
                         failed_message = f"Item not found on vendor server {vendor_url} (bought {successful_purchases} out of {amount_requested} requested)."
                         print(f"Vendor {vendor_url} reported 404 for item {item_id}.")
                         break # stop

                    else:
                         # some other http errors, catch-all
                         failed_message = f"Vendor server error (status {response.status_code}). Bought {successful_purchases} out of {amount_requested} requested."
                         print(f"Vendor server {vendor_url} returned unexpected status {response.status_code} for item {item_id}. Response: {response.text}")
                         break # also stop

                except requests.exceptions.ConnectionError as e:
                     failed_message = f"Communication error with vendor server {vendor_url}: {e} (bought {successful_purchases} out of {amount_requested} requested)."
                     print(f"Connection error buying {item_id} from {vendor_url}: {e}")
                     break
                except requests.exceptions.Timeout as e:
                     failed_message = f"Timeout communicating with vendor server {vendor_url}: {e} (bought {successful_purchases} out of {amount_requested} requested)."
                     print(f"Timeout buying {item_id} from {vendor_url}: {e}")
                     break
                except Exception as e:
                     failed_message = f"An unexpected error occurred during purchase attempt: {e} (bought {successful_purchases} out of {amount_requested} requested)."
                     print(f"Unexpected error during buy attempt for {item_id}: {e}")
                     break


            # summary of purchases, we can remove the requested vs successful stuff, its for debug purposes
            item_result = {
                'title': title,
                'requested_amount': amount_requested,
                'successful_amount': successful_purchases,
                'total_price_paid': total_price_paid,
                'success': successful_purchases == amount_requested, # true if all requested were bought
                'message': failed_message if failed_message else f"Successfully purchased {successful_purchases} units."
            }
            purchase_results.append(item_result)
            print(f"Finished processing buy for item ID {item_id}: Result - {item_result}")


        print("Finished processing all items in the buy request.")
        #xml-rpc does the conversion itself
        return purchase_results

if __name__ == '__main__':
    server = xmlrpc.server.SimpleXMLRPCServer(
        (MAIN_SERVER_HOST, MAIN_SERVER_PORT),
        allow_none=True # allows functions to return None if needed
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
    except Exception as e:
         print(f"An unexpected error occurred during server operation: {e}")
