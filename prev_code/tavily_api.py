from tavily import TavilyClient
import os

class TavilyAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = TavilyClient(api_key=self.api_key)

    def search(self, query):
        """
        Search for academic papers using Tavily API
        Args:
            query (str): Search query or citation to look up
        Returns:
            dict: Search results from Tavily
        """
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=True,
                include_images=False,
                max_results=5
            )
            return response
        except Exception as e:
            print(f"Error searching Tavily API: {str(e)}")
            return None
