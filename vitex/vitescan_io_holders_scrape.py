import requests
import json

import pandas as pd

try: from .. import settings
except: import settings


DATABASE = settings.FEED_API.VITESCAN_IO


class ViteScanHoldersScrape:

    @staticmethod
    def holders_updater():
        url = f"{DATABASE.BASE_URL}{DATABASE.HOLDERS_API_URL}"
        data = requests.get(url)

        if data.status_code == 200:
            holders = json.loads(data.content)['data']['accountsResults']
            with open('holders.json', 'w') as f:
                f.write(json.dumps(holders))

    @staticmethod
    def get_holders_stats():
        with open('holders.json', 'r') as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        balance_mean = df['totalBalance'].mean() / 10 ** 8
        dex_mean = df['dexAvailableBalance'].mean() / 10 ** 8
        dex_locked_mean = df['dexLockedBalance'].mean() / 10 ** 8

        response = {
            'balance_mean': balance_mean,
            'dex_mean': dex_mean,
            'dex_locked_mean': dex_locked_mean
            }

        return response

    @staticmethod
    def get_holders_summary(page=1):
        url = f"{DATABASE.BASE_URL}{DATABASE.HOLDERS_API_URL}&pageNo={page}"
        data = requests.get(url)

        if data.status_code == 200:
            data = json.loads(data.content)['data']
            response = {
                'total': data['total'],
                'top_10': [{
                    'rank': acc['rank'],
                    'address': acc['address'],
                    'balance': acc['totalBalance'],
                    'txs_count': acc['txnCount'],
                    'percentage': acc['percentage'],
                    } for acc in data['accountsResults'][:10]],
                'page_count': data['pageCount']
                }
            return response

        else:
            print(data)
