import json
import threading
import time

import requests
import _settings


class ExplorerScrapes:
    """
    Class to manage scrapes for Epic-Cash explorers/nodes.
    Each scrape is in single files in explorer dir, named by domain url.
    Multiple scripts are added for backup, response data should be always identical.
    Each new block is a new row in database contains blockchain state details:
    """
    from explorer.explorer_epic_tech import EpicTechScrape
    SCRAPES = [EpicTechScrape]
    DATABASE = _settings.Database
    INTERVAL = 5

    def run(self):
        print(f"STARTING EPIC EXPLORER SCRAPES...")
        while True:
            for scrape in self.SCRAPES:
                try:
                    block = scrape().get_last_update()
                    url = f"{self.DATABASE.API_URL}{self.DATABASE.API_GET_BLOCKS}"
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

            time.sleep(self.INTERVAL)


class VitexScrapes:
    """
    ViteScan.io scrape to get EPIC-002 holders stats
    """
    from vitex.vitescan_io_holders_scrape import ViteScanHoldersScrape
    SCRAPES = [ViteScanHoldersScrape]
    DATABASE = _settings.Database
    INTERVAL = 2 * 60

    def run(self):
        print(f"STARTING VITESCAN SCRAPE...")
        while True:
            for scrape in self.SCRAPES:
                try:
                    scrape().holders_updater()

                    summary = scrape().get_holders_summary()
                    stats = scrape().get_holders_stats()

                    response = {
                        'holders_count': summary['total'],
                        'holders_stats': stats
                        }

                    url = f"{self.DATABASE.API_URL}{self.DATABASE.API_GET_VITEX}"
                    response = requests.post(url=url, data=json.dumps(response),
                                             headers={'Content-Type': 'application/json'})

                    if response.status_code in [200, 201]:
                        print(f'DB RESPONSE [{response.status_code}] - Added new VitexUpdate')
                    else:
                        print(response.text)

                    print(f'Waiting [{self.INTERVAL} seconds]')

                except Exception as e:
                    print(e)
                    continue

            time.sleep(self.INTERVAL)


if __name__ == '__main__':
    explorer_scrapes = threading.Thread(target=ExplorerScrapes().run, daemon=True)
    vitex_scrapes = threading.Thread(target=VitexScrapes().run, daemon=True)

    explorer_scrapes.start()
    vitex_scrapes.start()

    explorer_scrapes.join()
    vitex_scrapes.join()

    print('Scrapes terminated.')
