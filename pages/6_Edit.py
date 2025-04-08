import streamlit as st
import pandas as pd
from firebase_utils import db, update_pdf_record
from datetime import datetime
from firebase_admin import firestore

st.set_page_config(
    page_title="Edit Data",
    page_icon="✏️",
    layout="wide"
)

st.title('✏️ Edit Database Records')

# Function to convert Firestore timestamp to datetime
def convert_timestamp(timestamp):
    if timestamp:
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return None

# Function to get collection data as DataFrame
def get_collection_df(collection_name):
    docs = list(db.collection(collection_name).stream())
    if not docs:
        return None
    
    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['id'] = doc.id
        for key, value in doc_dict.items():
            if 'timestamp' in key.lower() and value:
                doc_dict[key] = convert_timestamp(value)
        data.append(doc_dict)
    
    return pd.DataFrame(data)

# Create tabs for different collections
tab1, tab2 = st.tabs(["📄 Edit Files", "🔗 Edit References"])

with tab1:
    st.header("Edit PDF Files")
    files_df = get_collection_df('pdf_files')
    if files_df is not None:
        # Select file to edit
        file_id = st.selectbox(
            "Select File to Edit",
            options=files_df['file_id'].tolist(),
            format_func=lambda x: f"{x} ({files_df[files_df['file_id']==x]['status'].iloc[0]})"
        )
        
        if file_id:
            row = files_df[files_df['file_id'] == file_id].iloc[0]
            st.subheader(f"Editing: {file_id}")
            
            # Create form for editing
            with st.form(key=f"edit_file_{row['id']}"):
                # Status dropdown
                new_status = st.selectbox(
                    "Status",
                    options=['Initial', 'TextExtracted', 'TextProcessed'],
                    index=['Initial', 'TextExtracted', 'TextProcessed'].index(row['status'])
                )
                
                # Depth input
                new_depth = st.number_input(
                    "Depth",
                    min_value=1,
                    value=int(row.get('depth', 1))
                )
                
                # Reference count input (if exists)
                new_ref_count = None
                if 'reference_count' in row:
                    new_ref_count = st.number_input(
                        "Reference Count",
                        min_value=0,
                        value=int(row.get('reference_count', 0))
                    )
                
                # Submit button
                if st.form_submit_button("Save Changes"):
                    updates = {
                        'status': new_status,
                        'depth': new_depth,
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    }
                    if new_ref_count is not None:
                        updates['reference_count'] = new_ref_count
                        
                    try:
                        update_pdf_record(row['id'], updates)
                        st.success("Changes saved successfully!")
                        st.rerun()  # Refresh the page
                    except Exception as e:
                        st.error(f"Error saving changes: {str(e)}")
    else:
        st.info("No files found in the database")

with tab2:
    st.header("Edit References")
    refs_df = get_collection_df('references')
    if refs_df is not None:
        # Select reference to edit
        ref_id = st.selectbox(
            "Select Reference to Edit",
            options=refs_df['id'].tolist(),
            format_func=lambda x: f"{refs_df[refs_df['id']==x]['full_reference_text'].iloc[0][:100]}..."
        )
        
        if ref_id:
            row = refs_df[refs_df['id'] == ref_id].iloc[0]
            st.subheader(f"Editing Reference: {ref_id}")
            
            # Create form for editing
            with st.form(key=f"edit_ref_{ref_id}"):
                # Status dropdown
                new_status = st.selectbox(
                    "Status",
                    options=['NewReference', 'ProcessedReference'],
                    index=['NewReference', 'ProcessedReference'].index(row['status'])
                )
                
                # Reference text input
                new_ref_text = st.text_area(
                    "Reference Text",
                    value=row.get('full_reference_text', ''),
                    height=100
                )
                
                # Authors input
                new_authors = st.text_input(
                    "Authors",
                    value=row.get('authors', '')
                )
                
                # Title input
                new_title = st.text_input(
                    "Title",
                    value=row.get('title', '')
                )
                
                # Year input
                new_year = st.text_input(
                    "Year",
                    value=row.get('year', '')
                )
                
                # Submit button
                if st.form_submit_button("Save Changes"):
                    updates = {
                        'status': new_status,
                        'full_reference_text': new_ref_text,
                        'authors': new_authors,
                        'title': new_title,
                        'year': new_year,
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    }
                    
                    try:
                        db.collection('references').document(ref_id).update(updates)
                        st.success("Changes saved successfully!")
                        st.rerun()  # Refresh the page
                    except Exception as e:
                        st.error(f"Error saving changes: {str(e)}")
    else:
        st.info("No references found in the database")

# Add refresh button at the bottom
if st.button("🔄 Refresh Data"):
    st.rerun()
