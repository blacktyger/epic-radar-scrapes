"""
=================================================
HTTPS://EXPLORER.EPIC.TECH SCRAPE || VERSION: 0.1
=================================================
Scrape is connecting to official Epic-Cash Explorer API_URL,
data is streaming from explorer archive node (recommended as main scrape for feed)
"""

from scrapes import settings
from scrapes.explorer.base_scrape import ExplorerScrape


class EpicTechScrape(ExplorerScrape):
    api_url = settings.FEED_API.EXPLORER_EPIC_TECH.API_URL
    api_calls = settings.FEED_API.EXPLORER_EPIC_TECH.API_CALLS
    public_api_url = settings.FEED_API.EXPLORER_EPIC_TECH.PUBLIC_API_URL

    def _get_latest_block(self):
        url = f"{self.api_url}/{self.api_calls['latest_block']}"
        return self._request(url=url)

    def _get_block_by_height(self, height):
        url = f"{self.api_url}/{self.api_calls['block_by_height']}/{height}"
        return self._request(url=url)

    def get_last_update(self) -> dict:
        last_block = self._get_latest_block()

        if last_block['status'] == 200:
            last_block = last_block['response']

            network_hashrate = {
                'cuckoo': last_block['cuckoohashrate'],
                'progpow': last_block['progpowhashrate'],
                'randomx': last_block['randomxhashrate']
                }

            total_diffs = {
                'cuckoo': last_block['TotalDifficultyCuckatoo'],
                'progpow': last_block['TotalDifficultyProgpow'],
                'randomx': last_block['TotalDifficultyRandomx']
                }

            target_diffs = {
                'cuckoo': last_block['targetdifficultycuckatoo'],
                'progpow': last_block['targetdifficultyprogpow'],
                'randomx': last_block['targetdifficultyrandomx']
                }

            block_details = self._get_block_by_height(last_block['block_height'])

            if block_details['status'] == 200:
                block_details = block_details['response']['BlockchainBlockFetchQuery']

                avg_block_time = self._request(url=f"{self.public_api_url}average-blocktime")
                timestamp = self.str_to_timestamp(block_details['Timestamp'], frmt="%m-%d-%Y %H:%M:%S")

                block = {
                    'hash': block_details['Hash'],
                    'algo': block_details['Proof'].lower(),
                    'height': block_details['Height'],
                    'reward': block_details['BlockReward'],
                    'supply': last_block['coin_existence'],
                    'avg_time': avg_block_time,
                    'datetime': timestamp,
                    'timestamp': timestamp,
                    'total_diffs': total_diffs,
                    'target_diffs': target_diffs,
                    'network_hashrate': network_hashrate,
                    }

                return block
