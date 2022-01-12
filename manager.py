from datetime import datetime
import threading
import json
import time

import requests
import _settings


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
                    response = requests.post(url=url, data=json.dumps(block), headers={'Content-Type': 'application/json'})
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
                    response = requests.post(url=url, data=json.dumps(response),
                                             headers={'Content-Type': 'application/json'})

                    if response.status_code in [200, 201]:
                        print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                              f' - Added new VitexHolders [SLEEP: {self.INTERVAL}]')
                    else:
                        print(response.text)

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
    INTERVAL = 30

    def run(self):
        print(f"STARTING VITEX SCRAPE...")

        first = True  # To save historical snapshot in given interval

        while True:
            for scrape in self.SCRAPES:
                try:
                    ticker_update, history_update = scrape().get_update()

                    url = f"{self.DATABASE.API_URL}{self.DATABASE.API_GET_VITEX_UPDATE}"
                    response = requests.post(url=url, data=json.dumps(ticker_update),
                                             headers={'Content-Type': 'application/json'})

                    if response.status_code in [200, 201]:
                        print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                              f' - Added new VitexUpdate [SLEEP: {self.INTERVAL}]')
                    else:
                        print(response.text)

                    # Check against new hour
                    history_time = datetime.now().minute in [15, 16, 17, 18]

                    if history_time:
                        if first:
                            # If no history snapshot done yet
                            url = f"{self.DATABASE.API_URL}{self.DATABASE.API_GET_VITEX_HISTORY}"
                            response = requests.post(url=url, data=json.dumps(history_update),
                                                     headers={'Content-Type': 'application/json'})

                            if response.status_code in [200, 201]:
                                print(f'{log_time()} DB RESPONSE [{response.status_code}]'
                                      f' - Added new VitexHistory Snapshot')
                                first = False
                            else:
                                print(response.text)
                    else:
                        # Reset new hour flag
                        first = True

                except Exception as e:
                    print(f"VitexScrapes:\n{e}")
                    continue

            time.sleep(self.INTERVAL)


if __name__ == '__main__':
    explorer_scrapes = threading.Thread(target=ExplorerScrapes().run, daemon=True)
    vitescan_scrapes = threading.Thread(target=ViteScanScrapes().run, daemon=True)
    vitex_scrapes = threading.Thread(target=VitexScrapes().run, daemon=True)

    explorer_scrapes.start()
    vitescan_scrapes.start()
    vitex_scrapes.start()

    explorer_scrapes.join()
    vitescan_scrapes.join()
    vitex_scrapes.join()

    print(f'{log_time()} Scrapes terminated.')
