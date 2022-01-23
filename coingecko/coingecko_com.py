"""CoinGecko.com API scrape v0.1"""
import json

import requests

import _settings


class CoingeckoComScrape:
    API_URL = _settings.FEED_API.COINGECKO_COM.BASE_URL

    def _epic_vs_usd(self):
        try:
            url = f"{self.API_URL}/simple/price?ids=epic-cash&vs_currencies=usd"
            data = json.loads(requests.get(url).content)
            return float(data['epic-cash']['usd'])
        except json.JSONDecodeError as er:
            print(er)
            return 0

    def _epic_vs_btc(self):
        try:
            url = f"{self.API_URL}/simple/price?ids=epic-cash&vs_currencies=btc"
            data = json.loads(requests.get(url).content)
            return float(data['epic-cash']['btc'])
        except json.JSONDecodeError as er:
            print(er)
            return 0

    def _btc_vs_usd(self):
        try:
            return float(_settings.MarketData().price_btc_vs('usd'))
        except json.JSONDecodeError as er:
            print(er)
            return 0

    def update(self):
        epic_vs_usd = self._epic_vs_usd()
        epic_vs_btc = self._epic_vs_btc()
        btc_vs_usd = self._btc_vs_usd()

        return {'epic_vs_usd': epic_vs_usd, 'epic_vs_btc': epic_vs_btc,
                'btc_vs_usd': btc_vs_usd}