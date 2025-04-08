from langchain_community.tools import BraveSearch
import streamlit as st

def search_and_download_paper(paper_info, brave_api_key=st.secrets['BRAVE_API_KEY']):
    tool=BraveSearch(api_key=brave_api_key, search_kwargs={"num": 5})
