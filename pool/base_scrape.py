"""
base_scrape.py - template and base class for Epic-Cash explorer/node scrapes.
"""
import datetime
import json
import requests

import _settings

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


class PoolScrape:
    """Base class for Epic Pools scrapes, one scrape for one source"""
    api_url: str

    @staticmethod
    def _request(url):
        """Request API call and return dict data"""
        return requests.get(url).json()

    def _get_stats(self):
        pass

    def _get_blocks(self):
        pass