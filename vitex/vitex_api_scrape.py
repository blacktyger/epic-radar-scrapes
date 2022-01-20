from decimal import *

from .vitexpy import PublicAPI, Token, TradingPair
import _settings
import utils

getcontext().prec = 2


class VitexScrape:
    """Scrape and save to database EPIC-002_BTC-000 Vitex Exchange trading data"""
    PRICE_FEED = _settings.MarketData()
    API = PublicAPI()
    DB = _settings.Vitex

    BTC = Token(symbol=DB.BTC_SYMBOL)
    EPIC = Token(symbol=DB.EPIC_SYMBOL)
    EPIC_BTC = TradingPair(f"{DB.EPIC_SYMBOL}_{DB.BTC_SYMBOL}")

    def _get_data(self):
        ticker = self.API.get_trading_pair(self.EPIC_BTC)[0].meta

        changes = self.API.get_24hr_ticker_price_changes(self.BTC)
        changes = [pair for pair in changes if self.EPIC_BTC.symbol in pair['symbol']][0]

        trades = self.API.get_trade_history(pair=self.EPIC_BTC.symbol, **{'limit': 500})

        depth = self.API.get_order_book_depth(pair=self.EPIC_BTC.symbol)
        asks = depth['asks']
        bids = depth['bids']

        candles = self.API.get_candlestick_bars(pair=self.EPIC_BTC.symbol, interval='hour', limit=168)

        return ticker, changes, trades, asks, bids, candles

    @staticmethod
    def _parse_trades(trades_list):
        # Response template and list of transactions with some processing
        response = {'stats': {
            'bought': 0,
            'sold': 0,
            'highest': []
            }, 'list': [
            [trade['price'], round(float(trade['amount']), 4),
             (utils.t_s(trade['timestamp']).isoformat()),
             trade['side']] for trade in trades_list
            ]}

        # try:
        # Find all selling transactions
        sells = [float(buy[1]) for buy in response['list'] if buy[3] == 1]
        response['stats']['sold'] = sum(sells)

        # Find all buying transactions
        buys = [float(buy[1]) for buy in response['list'] if buy[3] == 0]
        response['stats']['bought'] = sum(buys)

        # Find the highest single sell and buy transaction
        try:
            response['stats']['highest'] = [max(buys), max(sells)]
        except:
            response['stats']['highest'] = [0,0]

            # except ValueError as er:
        #     print(er)

        return response

    def get_update(self):
        btc_usd = self.PRICE_FEED.price_btc_vs('USD')
        ticker, changes, trades_raw, asks, bids, raw_candles = self._get_data()

        trades_data = self._parse_trades(trades_list=trades_raw)

        candles = {
            'date': raw_candles['t'],
            'close': raw_candles['c'],
            'open': raw_candles['p'],
            'high': raw_candles['h'],
            'low': raw_candles['l'],
            'volume': raw_candles['v']
            }

        price = {
            'btc': ticker['lastPrice'],
            'usd': str(Decimal(btc_usd * Decimal(ticker['lastPrice']))),
            '24h_low': ticker['lowPrice'],
            '24h_high': ticker['highPrice'],
            }
        change = {
            '24h_percentage': round(float(changes['priceChangePercent']), 2),
            '24h_quota': '{:.8f}'.format(float(changes['priceChange'])),
            }
        volume = {
            'epic': round(float(ticker['volume']), 2),
            'btc': round(float(ticker['baseVolume']), 2),
            'usd': round(float(btc_usd) * float(ticker['baseVolume']), 2)
            }
        trades = {
            'stats': trades_data['stats'],
            'list': trades_data['list']
            }

        ticker_update = {'price': price, 'change': change, 'volume': volume,
                         'bids': bids, 'asks': asks, 'trades': trades,
                         'candles': candles, 'tickers': ticker}

        history_update = {'price': price, 'volume': volume, 'trades': trades}

        return ticker_update, history_update
