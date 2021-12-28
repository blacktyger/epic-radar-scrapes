"""
base_scrape.py - template and base class for Epic-Cash explorer/node scrapes.
"""
import datetime
import json
import requests
import settings


"""RESPONSE TEMPLATE:

response = {
    'hash': 
    'algo': 
    'height': 
    'reward': 
    'supply': 
    'avg_time': 
    'datetime':
    'timestamp': 
    'total_diffs': 
    'target_diffs': 
    'network_hashrate': 
}"""


class ExplorerScrape:
    """Base class for Epic explorers scrapes, one scrape for one source
    """
    algos: list = settings.Blockchain.ALGORITHMS
    api_url: str
    api_calls: dict

    @staticmethod
    def _request(url):
        """Request API call and return dict data"""
        return json.loads(requests.get(url).content)

    def get_last_block(self) -> dict:
        """Make all API calls and collect data, return dict"""
        pass

    @staticmethod
    def str_to_timestamp(date_str: str, frmt: str) -> int:
        """Take date string and format, return timestamp"""
        date, time = date_str.split(',')
        time = time.split(' ')[1]
        dt = datetime.datetime.strptime(f"{date} {time}", frmt)
        return int(dt.timestamp())