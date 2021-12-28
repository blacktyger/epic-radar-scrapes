"""
ViteScan.io scrape to get EPIC-002 holders stats
"""

import json
import time

import requests

from scrapes import settings
from scrapes.vitex.vitescan_io_holders_scrape import ViteScanHoldersScrape

SCRAPES = [ViteScanHoldersScrape]
DATABASE = settings.Database
INTERVAL = 2*60


def main():
    print(f"STARTING VITESCAN SCRAPE...")
    while True:
        for scrape in SCRAPES:
            try:
                scrape().holders_updater()

                summary = scrape().get_holders_summary()
                stats = scrape().get_holders_stats()

                response = {
                    'holders_count': summary['total'],
                    'holders_stats': stats
                    }

                url = f"{DATABASE.API_URL}{DATABASE.API_GET_VITEX}"
                response = requests.post(url=url, data=json.dumps(response), headers={'Content-Type': 'application/json'})

                if response.status_code in [200, 201]:
                    print(f'DB RESPONSE [{response.status_code}] - Added new VitexUpdate')
                else:
                    print(response.text)

                print(f'Waiting [{INTERVAL} seconds]')

            except Exception as e:
                print(e)
                continue

        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()