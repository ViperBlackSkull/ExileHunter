#!/usr/bin/env python3

import argparse
import requests
import csv
import random
import time
import os
from datetime import datetime
from itertools import islice
from http import HTTPStatus

class PoETradeAPI:
    def __init__(self, league="Standard", debug=False):
        self.post_url = f"https://www.pathofexile.com/api/trade2/search/poe2/{league}"
        self.get_url = "https://www.pathofexile.com/api/trade2/fetch/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.debug = debug

    def debug_log(self, message):
        if self.debug:
            print(f"[{datetime.now()}] [DEBUG] {message}")

    def send_post_request(self, url, payload):
        while True:
            try:
                response = requests.post(url, headers=self.headers, json=payload)
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    self.handle_rate_limit()
                    continue
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"[{datetime.now()}] Error: {e}. Retrying later...")
                time.sleep(random.uniform(120, 180))

    def send_get_request(self, url):
        while True:
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    self.handle_rate_limit()
                    continue
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"[{datetime.now()}] Error: {e}. Retrying later...")
                time.sleep(random.uniform(120, 180))

    def handle_rate_limit(self):
        sleep_time = random.uniform(120, 180)
        print(f"[{datetime.now()}] Rate limit encountered. Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    def chunked_iterable(self, iterable, size):
        it = iter(iterable)
        for first in it:
            yield [first] + list(islice(it, size - 1))

    def fetch_item_ids(self, search_payload):
        data = self.send_post_request(self.post_url, search_payload)
        total_items = data.get("total", 0)
        print(f"[{datetime.now()}] Total items listed for search: {total_items}")
        return data.get("result", [])

    def fetch_item_details_in_batches(self, item_ids, batch_size=10):
        all_details = []
        for batch in self.chunked_iterable(item_ids, batch_size):
            item_ids_str = ",".join(batch)
            full_url = f"{self.get_url}{item_ids_str}"
            try:
                response_data = self.send_get_request(full_url)
                all_details.extend(response_data.get("result", []))
                sleep_time = random.uniform(15, 60)
                print(f"[{datetime.now()}] Throttling: Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            except requests.exceptions.RequestException as e:
                print(f"[{datetime.now()}] Error fetching batch: {batch}, Error: {e}")
                time.sleep(random.uniform(15, 60))
        return all_details

    def parse_trade_data(self, data):
        parsed_results = []
        for item in data:
            listing = item.get("listing", {})
            item_data = item.get("item", {})
            explicit_mods = "; ".join(item_data.get("explicitMods", []))
            enchant_mods = "; ".join(item_data.get("enchantMods", []))
            parsed_results.append({
                "Item Name": f"{item_data.get('name', 'Unknown')} {item_data.get('typeLine', '')}",
                "Price": f"{listing.get('price', {}).get('amount', 'Unknown')} {listing.get('price', {}).get('currency', 'Unknown')}",
                "Seller": listing.get("account", {}).get("name", "Unknown"),
                "League": item_data.get("league", "Unknown"),
                "Corrupted": item_data.get("corrupted", False),
                "Item Level": item_data.get("ilvl", "Unknown"),
                "Explicit Mods": explicit_mods,
                "Enchant Mods": enchant_mods,
                "Whisper Message": listing.get("whisper", ""),
            })
        return parsed_results

    def save_to_csv(self, data, filename, append=False):
        if not data:
            print(f"[{datetime.now()}] No data to save.")
            return

        headers = data[0].keys()
        mode = "a" if append else "w"
        os.makedirs("outputs", exist_ok=True)
        file_path = os.path.join("outputs", filename)
        with open(file_path, mode=mode, newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            if not append:
                writer.writeheader()
            writer.writerows(data)
        print(f"[{datetime.now()}] Data {'appended to' if append else 'saved to'} {file_path}")

    def search_items(self, item_name, price_range):
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{item_name}_{today}.csv"
        first_iteration = True

        for price in price_range:
            print(f"[{datetime.now()}] Fetching items with price: {price} divine")
            search_payload = {
                "query": {
                    "status": {"option": "online"},
                    "name": item_name,
                    "filters": {
                        "trade_filters": {
                            "disabled": False,
                            "filters": {
                                "price": {"option": "divine", "min": price, "max": price}
                            }
                        }
                    }
                },
                "sort": {"price": "asc"},
            }

            try:
                item_ids = self.fetch_item_ids(search_payload)
                if not item_ids:
                    print(f"[{datetime.now()}] No items found for price: {price} divine.")
                    time.sleep(random.uniform(15, 60))
                    continue

                print(f"[{datetime.now()}] Found {len(item_ids)} items for price: {price} divine.")
                item_details = self.fetch_item_details_in_batches(item_ids, batch_size=10)
                parsed_data = self.parse_trade_data(item_details)
                self.save_to_csv(parsed_data, filename, append=not first_iteration)
                first_iteration = False
            except Exception as e:
                print(f"[{datetime.now()}] An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(description="Search for items in Path of Exile trade API.")
    parser.add_argument("-s", "--search", type=str, required=True, help="Item name to search for.")
    parser.add_argument("-l", "--league", type=str, default="Standard", help="League name to search in.")
    parser.add_argument("--debug", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    api = PoETradeAPI(league=args.league, debug=args.debug)
    price_range = range(1, 2)  # Define the price range in divines
    api.search_items(args.search, price_range)

if __name__ == "__main__":
    main()
