from datetime import datetime
import threading
import json
import time
import sys

import requests
import _settings

if 'win' in sys.platform:
    auth_token = "cbb072c17048624e608e349bb4de6c94cb97a78c"
else:
    auth_token = "99857427747756a08db271b4f34941030342b75c"

headers = {'Authorization': f"Token {auth_token}", 'Content-Type': 'application/json'}

def log_time():
    return f"{datetime.now().day}/{datetime.now().month} {str(datetime.now().time()).split('.')[0]}: "


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
                    response = requests.post(url=url, data=json.dumps(block), headers=headers)
                    if response.status_code == 201:
                        print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                              f' - Added new block [{block["height"]}] [SLEEP: {self.INTERVAL}]')
                    else:
                        if 'height' in json.loads(response.content).keys():
                            pass
                            # print(f'DB RESPONSE [{response.status_code}] - Block [{block["height"]}] already in database')
                        else:
                            print(f"{log_time()} DB RESPONSE [{response.status_code}] ", json.loads(response.content))
                except Exception as e:
                    print(f"ExplorerScrapes:\n{e}")
                    continue

            time.sleep(self.INTERVAL)


class ViteScanScrapes:
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

                    url = f"{self.DATABASE.API_URL}{self.DATABASE.API_GET_VITEX_HOLDERS}"
                    response = requests.post(url=url, headers=headers, data=json.dumps(response))

                    if response.status_code in [200, 201]:
                        print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                              f' - Added new VitexHolders [SLEEP: {self.INTERVAL}]')
                    else:
                        print('VitexScan:', response.text)

                except Exception as e:
                    print(f"VitexScan:\n{e}")
                    continue

            time.sleep(self.INTERVAL)


class VitexScrapes:
    """
    Vitex.net scrapes to get EPIC-002 DEX trading data
    """
    from vitex.vitex_api_scrape import VitexScrape
    SCRAPES = [VitexScrape]
    DATABASE = _settings.Database
    UPDATE_INTERVAL = 30
    HISTORY_INTERVAL = 60 * 60

    def run(self):
        print(f"STARTING VITEX SCRAPE...")

        first = True  # To save historical snapshot in given interval

        while True:
            for scrape in self.SCRAPES:
                try:
                    ticker_update, history_update = scrape().get_update()

                    url = f"{self.DATABASE.API_URL}{self.DATABASE.API_GET_VITEX_UPDATE}"
                    response = requests.post(url=url, data=json.dumps(ticker_update), headers=headers)

                    if response.status_code in [200, 201]:
                        print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                              f' - Added new VitexUpdate [SLEEP: {self.UPDATE_INTERVAL}]')
                    else:
                        print(response.text)

                    # Check against new hour
                    history_time = datetime.now().minute in [0, 1]

                    if history_time:
                        if first:
                            # If no history snapshot done yet
                            url = f"{self.DATABASE.API_URL}{self.DATABASE.API_GET_VITEX_HISTORY}"
                            response = requests.post(url=url, data=json.dumps(history_update), headers=headers)

                            if response.status_code in [200, 201]:
                                print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                                      f' - Added new VitexHistory Snapshot [SLEEP: {self.HISTORY_INTERVAL}]')
                                first = False
                            else:
                                print('VitexScrapes:', response.text)
                    else:
                        # Reset new hour flag
                        first = True

                except Exception as e:
                    print(f"VitexScrapes:\n{e}")
                    continue

            time.sleep(self.UPDATE_INTERVAL)


class CoingeckoScrapes:
    """
    Coingecko.com scrapes to get EPIC trading data
    """
    from coingecko.coingecko_com import CoingeckoComScrape
    SCRAPES = [CoingeckoComScrape]
    DATABASE = _settings.Database
    UPDATE_INTERVAL = 30

    def run(self):
        print(f"STARTING COINGECKO SCRAPE...")

        while True:
            for scrape in self.SCRAPES:
                try:
                    epic_vs_ = scrape().update()
                    url = f"{self.DATABASE.API_URL}{self.DATABASE.COINGECKO}"
                    response = requests.post(url=url, data=json.dumps(epic_vs_), headers=headers)

                    if response.status_code in [200, 201]:
                        print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                              f' - Added new COINGECKO Update [SLEEP: {self.UPDATE_INTERVAL}]')
                    else:
                        print('COINGECKO:', response.text)

                except Exception as e:
                    print(f"COINGECKO:\n{e}")
                    continue

            time.sleep(self.UPDATE_INTERVAL)


if __name__ == '__main__':
    coingecko_scrapes = threading.Thread(target=CoingeckoScrapes().run, daemon=True)
    explorer_scrapes = threading.Thread(target=ExplorerScrapes().run, daemon=True)
    vitescan_scrapes = threading.Thread(target=ViteScanScrapes().run, daemon=True)
    vitex_scrapes = threading.Thread(target=VitexScrapes().run, daemon=True)

    vitex_scrapes.start()
    explorer_scrapes.start()
    vitescan_scrapes.start()
    coingecko_scrapes.start()

    vitex_scrapes.join()
    explorer_scrapes.join()
    vitescan_scrapes.join()
    coingecko_scrapes.join()

    print(f'{log_time()} Scrapes terminated.')
