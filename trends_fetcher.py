from typing import Dict, List
from pytrends.request import TrendReq
from googlesearch import search
import requests
import logging

class TrendsFetcher:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.crawling_api_base_url = "https://firefox-rm.azurewebsites.net/api/httpTriggerParser"
        self.max_crawled_results = 3

    async def _get_crawled_data(self, url: str) -> Dict:
        """Helper method to fetch crawled data for a URL"""
        try:
            api_url = f"{self.crawling_api_base_url}?url={url}"
            response = requests.get(api_url)
            if response.status_code == 200:
                crawled_data = response.json()
                crawled_data["url"] = url
                return crawled_data
            else:
                logging.warning(f"Crawling failed for URL {url} with status code: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Error crawling URL {url}: {str(e)}")
            return None

    async def _process_search_results(self, trend_title: str) -> tuple[List[Dict], List[Dict]]:
        """Helper method to process search results and get crawled data"""
        search_results = []
        crawled_data_list = []
        
        search_query = f"{trend_title} latest news"
        data = search(search_query, advanced=True)

        for result in data:
            if len(crawled_data_list) >= self.max_crawled_results:
                break

            search_result = {
                'url': result.url,
                'title': result.title,
                'description': result.description
            }
            search_results.append(search_result)

            crawled_data = await self._get_crawled_data(result.url)
            if crawled_data:
                crawled_data_list.append(crawled_data)

        return search_results, crawled_data_list

    async def get_trending_topics(self) -> List[Dict]:
        """
        Fetches current trending topics from Google Trends with related search results
        Returns: List of trending topics with their metadata and search results
        """
        try:
            raw_data = []
            trends = self.pytrends.trending_searches(pn='india')

            for sno, title in trends.itertuples():
                search_results, crawled_data = await self._process_search_results(title)
                
                trend_data = {
                    'sno': sno,
                    'trend_title': title,
                    'search_results': search_results,
                    'crawled_data': crawled_data
                }
                raw_data.append(trend_data)

            return raw_data

        except Exception as e:
            logging.error(f"Error fetching trends: {str(e)}")
            raise Exception(f"Error fetching trends: {str(e)}")
