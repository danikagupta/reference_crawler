import streamlit as st
import requests
import json
import tempfile
from urllib.parse import quote_plus
from firebase_utils import upload_pdf_to_storage, add_pdf_record

def search_and_download_paper(paper_info, serp_api_key=st.secrets['SERP_API_KEY']):
    """Search for a paper and download it to Firebase Storage
    
    Args:
        paper_info (str)
        serp_api_key (str): API key for serpstack
        
    Returns:
        str: File ID of the downloaded paper, or None if not found
    """
    try:
        query = f"Searching for paper {paper_info} filetype:pdf"
        st.sidebar.write(query)
        
        # SERP API endpoint
        url = "https://api.serpstack.com/search"
        
        # Parameters for the SERP API request
        params = {
            "access_key": serp_api_key,
            "query": query,
            "num": 5,  # Number of results to retrieve
        }
    
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        print(f"{search_results=}")
        
        
        # Check if we have any organic results
        if 'organic_results' in search_results and search_results['organic_results']:
            for result in search_results['organic_results']:
                st.sidebar.write(result)
                pdf_url = result.get('url')
                if pdf_url and pdf_url.lower().endswith('.pdf'):
                    # Attempt to download the PDF
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        # Generate a filename
                        file_id = f"{quote_plus(paper_info[:200])}.pdf"
                        
                        # Save to Firebase Storage
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            temp_file.write(pdf_response.content)
                            temp_file.seek(0)  # Rewind to start of file
                            # Upload to Firebase Storage
                            upload_pdf_to_storage(temp_file, file_id)
                        
                        # Add record to Firestore
                        add_pdf_record(file_id)
                        
                        st.success(f"PDF downloaded and saved: {file_id}")
                        return file_id
            
            st.warning(f"No suitable PDF link found in the search results for {paper_info}.")
        else:
            st.warning(f"No search results found for {paper_info}.")
    
    except Exception as e:
        st.error(f"An error occurred during the search: {e}")
    
    return None
