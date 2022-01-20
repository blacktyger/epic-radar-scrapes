"""
=================================================
HTTPS://ICEMINING.CA SCRAPE || VERSION: 0.1
=================================================
SCRAPE IS CONNECTING TO OFFICIAL ICEMINING.CA API
AND PROCESS AVAILABLE DATA
"""
import requests

from _settings import Mining


class IceminingCaScrape:
    API_URL = Mining.POOLS['icemining']['api']
    methods = ['currencies/', 'blocks/epic']

    def get_stats(self):
        url = f"{self.API_URL}{self.methods[0]}"
        try:
            response = requests.get(url).json()['EPIC']
            print(response['EPIC'])
        except Exception as e:
            print(e)
            return None




i = IceminingCaScrape()
i.get_stats()