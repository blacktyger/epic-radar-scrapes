from decimal import *

from .vitexpy import PublicAPI, Token, TradingPair
import _settings

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

        trades = self.API.get_trade_history(pair=self.EPIC_BTC.symbol, **{'limit': 100})

        depth = self.API.get_order_book_depth(pair=self.EPIC_BTC.symbol)
        asks = depth['asks']
        bids = depth['bids']

        candles = self.API.get_candlestick_bars(pair=self.EPIC_BTC.symbol, interval='day')

        return ticker, changes, trades, asks, bids, candles

    def get_update(self):
        ticker, changes, trades, asks, bids, candles = self._get_data()
        btc_usd = self.PRICE_FEED.price_btc_vs('USD')

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

        ticker_update = {'price': price, 'change': change, 'volume': volume,
                         'bids': bids, 'asks': asks, 'trades': trades,
                         'candles': candles, 'tickers': ticker}

        history_update = {'price': price, 'volume': volume, 'trades': trades}

        return ticker_update, history_update

