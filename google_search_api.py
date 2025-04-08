import streamlit as st

import os

from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper


def search_and_get_paper_links(paper_info, google_api_key=st.secrets['GOOGLE_API_KEY'], google_cse_id=st.secrets['GOOGLE_CSE_ID']):
    """Search for papers and return their URLs and titles.
    
    Args:
        paper_info (str): The paper information to search for
        google_api_key (str): Google Custom Search API key
        google_cse_id (str): Google Custom Search Engine ID
        
    Returns:
        list[dict]: List of dictionaries containing 'url' and 'title' for each result
    """
    print(f"Searching for {paper_info}\n***********\n\n\n")
    os.environ["GOOGLE_CSE_ID"] = google_cse_id
    os.environ["GOOGLE_API_KEY"] = google_api_key
    
    tool = GoogleSearchAPIWrapper(k=5)
    results = tool.results(f"{paper_info} filetype:pdf", num_results=5)
    
    search_results = []
    for result in results:
        print(f"Result: {result}")
        search_results.append({
            'url': result['link'],
            'title': result.get('title', '').replace(' PDF', '').strip()  # Clean up title
        })
    
    return search_results