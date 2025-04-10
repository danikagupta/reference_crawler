import streamlit as st
import pandas as pd
import tempfile
from firebase_utils import db, download_pdf_from_storage, download_txt_from_storage
from datetime import datetime

st.set_page_config(
    page_title="View Data",
    page_icon="👀",
    layout="wide"  # Use wide layout for better table display
)

st.title('👀 View Database Contents')

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
    
    # Convert documents to list of dicts
    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['id'] = doc.id  # Add document ID
        # Convert timestamps
        for key, value in doc_dict.items():
            if 'timestamp' in key.lower() and value:
                doc_dict[key] = convert_timestamp(value)
        data.append(doc_dict)
    
    return pd.DataFrame(data)

# Create tabs for different collections
tab1, tab2, tab3 = st.tabs(["📄 Files", "🔗 References", "🔍 Triplets"])

with tab1:
    st.header("PDF Files")
    files_df = get_collection_df('pdf_files')
    if files_df is not None:
        # Reorder columns to show important ones first
        cols = ['id', 'file_id', 'status', 'depth', 'reference_count', 
                'created_timestamp', 'updated_timestamp', 'txt_file_location']
        cols = [col for col in cols if col in files_df.columns] + \
               [col for col in files_df.columns if col not in cols]
        files_df = files_df[cols]
        
        # Add filters
        st.subheader("Filters")
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=sorted(files_df['status'].unique()),
                default=[]
            )
        with col2:
            search_term = st.text_input("Search in File IDs", "")
        
        # Apply filters
        filtered_df = files_df
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if search_term:
            filtered_df = filtered_df[filtered_df['file_id'].str.contains(search_term, case=False, na=False)]
        
        # Show dataframe with row numbers
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=False
        )
        st.caption(f"Showing {len(filtered_df)} of {len(files_df)} files")

        # Add download section below the table
        st.subheader("Download Files")
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter qualified papers for dropdown
            qualified_df = filtered_df[filtered_df['qualified'] == True]
            file_id = st.selectbox(
                "Select File",
                options=qualified_df['file_id'].tolist(),
                format_func=lambda x: qualified_df[qualified_df['file_id']==x]['title'].iloc[0] 
                    if not pd.isna(qualified_df[qualified_df['file_id']==x]['title'].iloc[0]) 
                    else x)
        
        if file_id:
            row = filtered_df[filtered_df['file_id'] == file_id].iloc[0]
            with col2:
                st.write("Download Options:")
                download_col1, download_col2 = st.columns(2)
                
                with download_col1:
                    if st.button("📄 Download PDF", key=f"pdf_{row['id']}"):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                download_pdf_from_storage(row['file_id'], tmp_file)
                                with open(tmp_file.name, 'rb') as f:
                                    st.download_button(
                                        label="📄 Save PDF",
                                        data=f,
                                        file_name=f"{row.get('title', row['file_id'])}.pdf",
                                        mime='application/pdf',
                                        key=f"save_pdf_{row['id']}"
                                    )
                        except Exception as e:
                            st.error(f"Error downloading PDF: {str(e)}")
                
                with download_col2:
                    if row.get('txt_file_location') and st.button("📝 Download TXT", key=f"txt_{row['id']}"):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                download_txt_from_storage(row['file_id'], tmp_file)
                                with open(tmp_file.name, 'rb') as f:
                                    st.download_button(
                                        label="📝 Save TXT",
                                        data=f,
                                        file_name=f"{row.get('title', row['file_id'])}.txt",
                                        mime='text/plain',
                                        key=f"save_txt_{row['id']}"
                                    )
                        except Exception as e:
                            st.error(f"Error downloading TXT: {str(e)}")
    else:
        st.info("No files found in the database")

with tab2:
    st.header("References")
    refs_df = get_collection_df('references')
    if refs_df is not None:
        # Reorder columns to show important ones first
        cols = ['id', 'full_citation', 'source_file', 'status',
                'created_timestamp', 'updated_timestamp']
        cols = [col for col in cols if col in refs_df.columns] + \
               [col for col in refs_df.columns if col not in cols]
        refs_df = refs_df[cols]
        
        # Add filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=sorted(refs_df['status'].unique()),
                default=[]
            )
        with col2:
            source_filter = st.multiselect(
                "Filter by Source File",
                options=sorted(refs_df['source_file'].unique()),
                default=[]
            )
        with col3:
            search_term = st.text_input("Search in Citations", "")
        
        # Apply filters
        filtered_df = refs_df
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if source_filter:
            filtered_df = filtered_df[filtered_df['source_file'].isin(source_filter)]
        if search_term:
            filtered_df = filtered_df[filtered_df['full_citation'].str.contains(search_term, case=False, na=False)]
        
        # Show dataframe with row numbers
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=False
        )
        st.caption(f"Showing {len(filtered_df)} of {len(refs_df)} references")
    else:
        st.info("No references found in the database")

# Add triplets tab content
with tab3:
    st.header("Triplets Group A")
    triplets_df = get_collection_df('triplets_group_a')
    if triplets_df is not None:
        # Reorder columns to show important ones first
        cols = ['id', 'title', 'file_id', 'subject', 'predicate', 'object',
                'created_timestamp']
        cols = [col for col in cols if col in triplets_df.columns] + \
               [col for col in triplets_df.columns if col not in cols]
        triplets_df = triplets_df[cols]
        
        # Add filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        with col1:
            title_filter = st.multiselect(
                "Filter by Paper Title",
                options=sorted(triplets_df['title'].unique()),
                default=[]
            )
        with col2:
            subject_search = st.text_input("Search in Subject", "")
        with col3:
            object_search = st.text_input("Search in Object", "")
        
        # Apply filters
        filtered_df = triplets_df
        if title_filter:
            filtered_df = filtered_df[filtered_df['title'].isin(title_filter)]
        if subject_search:
            filtered_df = filtered_df[filtered_df['subject'].str.contains(subject_search, case=False, na=False)]
        if object_search:
            filtered_df = filtered_df[filtered_df['object'].str.contains(object_search, case=False, na=False)]
        
        # Show dataframe with row numbers
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=False
        )
        st.caption(f"Showing {len(filtered_df)} of {len(triplets_df)} triplets")
    else:
        st.info("No triplets found in the database")

# Add refresh button at the bottom
if st.button("🔄 Refresh Data"):
    st.rerun()
