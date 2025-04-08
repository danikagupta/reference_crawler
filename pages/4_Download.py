import streamlit as st
import pandas as pd
from firebase_utils import db
import json
from datetime import datetime

st.set_page_config(
    page_title="Download Data",
    page_icon="💾",
)

st.title('💾 Download Data')

st.markdown("""
Export your processed data in various formats:
- Paper information
- Reference networks
- Processing statistics
""")

# Function to get all documents from a collection
def get_collection_data(collection_name):
    docs = db.collection(collection_name).stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]

# Download Papers
if st.button('Download Papers Data'):
    papers_data = get_collection_data('pdf_files')
    if papers_data:
        df = pd.DataFrame(papers_data)
        csv = df.to_csv(index=False)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button(
            label="Download Papers CSV",
            data=csv,
            file_name=f'papers_{timestamp}.csv',
            mime='text/csv',
        )
    else:
        st.info('No paper data available.')

# Download References
if st.button('Download References Data'):
    refs_data = get_collection_data('references')
    if refs_data:
        df = pd.DataFrame(refs_data)
        csv = df.to_csv(index=False)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button(
            label="Download References CSV",
            data=csv,
            file_name=f'references_{timestamp}.csv',
            mime='text/csv',
        )
    else:
        st.info('No reference data available.')

# Download Full Dataset
if st.button('Download Complete Dataset (JSON)'):
    full_data = {
        'papers': get_collection_data('pdf_files'),
        'references': get_collection_data('references'),
        'export_date': datetime.now().isoformat()
    }
    if full_data['papers'] or full_data['references']:
        json_str = json.dumps(full_data, indent=2)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button(
            label="Download Complete Dataset",
            data=json_str,
            file_name=f'reference_crawler_export_{timestamp}.json',
            mime='application/json',
        )
    else:
        st.info('No data available for export.')
