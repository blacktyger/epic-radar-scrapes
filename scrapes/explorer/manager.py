"""
manager.py - Script to manage scrapes for Epic-Cash explorers/nodes.
Each scrape is in single files in explorer_scrapes dir, named by domain url.
Multiple scripts are added for backup, response data should be always identical.
Each new block is a new row in database contains blockchain state details:
"""

import json
import time

import requests

from scrapes import settings
from scrapes.explorer.explorer_epic_tech import EpicTechScrape

SCRAPES = [EpicTechScrape]
DATABASE = settings.Database
INTERVAL = 5


def main():
    print(f"STARTING EPIC EXPLORER SCRAPES...")
    while True:
        for scrape in SCRAPES:
            try:
                block = scrape().get_last_update()
                url = f"{DATABASE.API_URL}{DATABASE.API_GET_BLOCKS}"
                response = requests.post(url=url, data=json.dumps(block), headers={'Content-Type': 'application/json'})
                if response.status_code == 201:
                    print(f'DB RESPONSE [{response.status_code}] - Added new block [{block["height"]}]')
                else:
                    if 'height' in json.loads(response.content).keys():
                        print(f'DB RESPONSE [{response.status_code}] - Block [{block["height"]}] already in database')
                    else:
                        print(f" DB RESPONSE [{response.status_code}] ", json.loads(response.content))
            except Exception as e:
                print(e)
                continue

        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()