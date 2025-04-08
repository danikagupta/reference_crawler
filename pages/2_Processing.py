import streamlit as st
import tempfile
import requests
import hashlib
import datetime
from firebase_utils import (
    db, download_pdf_from_storage, update_pdf_record,
    upload_txt_to_storage, download_txt_from_storage,
    upload_pdf_to_storage, download_text_from_storage
)
from firebase_admin import firestore
from main import extract_text_from_pdf, extract_references_from_text
from google_search_api import search_and_get_paper_links
from qualify_paper import qualify_paper
from langchain_openai import ChatOpenAI

st.set_page_config(
    page_title="Process Papers",
    page_icon="⚙️",
)

st.title('⚙️ Process Papers')

st.markdown("""
This page handles the processing pipeline for your uploaded papers:
1. Text Extraction - Extract text from PDFs and save to files
2. Reference Processing - Analyze saved text files to extract references
3. Reference Crawling - Search and download referenced papers
""")

st.divider()
# Text Extraction Section
col1, col2 = st.columns([1, 3])
with col1:
    extract_limit = st.number_input('Number of PDFs to process', min_value=1, value=1, step=1, key='extract_limit')
with col2:
    if st.button('Extract Text from PDFs'):
        with st.spinner('Extracting text from PDFs...'):
            # Fetch initial records
            docs = db.collection('pdf_files').where('status', '==', 'Initial').limit(extract_limit).stream()
            processed = 0
        for doc in docs:
            try:
                file_data = doc.to_dict()
                # Download PDF from Firebase Storage
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    download_pdf_from_storage(file_data['file_id'], temp_file)
                    # Extract text from PDF
                    text_content = extract_text_from_pdf(temp_file.name)
                    # Save extracted text to Firebase Storage
                    txt_url = upload_txt_to_storage(text_content, file_data['file_id'])
                    # Update Firestore record
                    update_pdf_record(doc.id, {
                        'status': 'TextExtracted',
                        'txt_file_location': txt_url,
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    })
                    processed += 1
            except Exception as e:
                st.error(f"Error processing {file_data.get('file_id', 'unknown file')}: {str(e)}")
                # Update status to failed
                update_pdf_record(doc.id, {
                    'status': 'FailedProcessing',
                    'error_message': str(e),
                    'updated_timestamp': firestore.SERVER_TIMESTAMP
                })
                continue
        if processed > 0:
            st.success(f'Extracted text from {processed} PDF(s) successfully.')
        else:
            st.info('No new PDFs to process.')

# Qualify Papers Section
st.divider()
col1, col2 = st.columns([1, 3])
with col1:
    qualify_limit = st.number_input('Number of papers to qualify', min_value=1, value=1, step=1, key='qualify_limit')
    qualify_button = st.button('Qualify Papers')
with col2:
    if qualify_button:
        # Get papers that haven't been qualified yet
        # Create a query for papers with either TextExtracted or TextProcessed status
        # and no qualified field or qualified=None
        papers = []
        query = db.collection('pdf_files')
        query = query.where('status', 'in', ['TextExtracted', 'TextProcessed'])
        query = query.limit(qualify_limit)
        
        for doc in query.stream():
            doc_data = doc.to_dict()
            # Include if qualified field is missing or None
            if 'qualified' not in doc_data or doc_data['qualified'] is None:
                papers.append(doc)
        
        st.write(f"Found {len(papers)} unqualified papers")
        
        if papers:
            llm = ChatOpenAI(
                openai_api_key=st.secrets['OPENAI_API_KEY'],
                model_name='gpt-4-turbo-preview',
                temperature=0
            )
            
            processed = 0
            progress_bar = st.progress(0)
            
            for i, doc in enumerate(papers):
                doc_data = doc.to_dict()
                st.write(f"Qualifying paper: {doc_data.get('title', doc_data['file_id'])}")
                
                try:
                    # Get the extracted text from Firebase Storage
                    text_content = download_text_from_storage(doc_data['file_id'])
                    
                    # Qualify the paper
                    is_qualified = qualify_paper(text_content, llm)
                    
                    # Update the paper's qualification status
                    update_pdf_record(doc.id, {
                        'qualified': is_qualified,
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    })
                    processed += 1
                except Exception as e:
                    st.error(f"Error qualifying paper {doc_data['file_id']}: {str(e)}")
                    # Update status to failed
                    update_pdf_record(doc.id, {
                        'status': 'FailedProcessing',
                        'error_message': str(e),
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    })
                finally:
                    progress_bar.progress((i + 1) / len(papers))
            
            st.success(f'Qualified {processed} paper(s).')
        else:
            st.info('No papers ready for qualification.')

# Process References Section
st.divider()

col1, col2 = st.columns([1, 3])
with col1:
    process_limit = st.number_input('Number of files to process', min_value=1, value=1, step=1, key='process_limit')
with col2:
    if st.button('Process References'):
        with st.spinner('Processing references...'):
            # Get qualified documents ready for processing
            query = db.collection('pdf_files')
            query = query.where('status', '==', 'TextExtracted')
            query = query.where('qualified', '==', True)  # Only process qualified papers
            query = query.limit(process_limit)
            papers = list(query.stream())
            processed = 0
        for doc in papers:
            try:
                file_data = doc.to_dict()
                # Download text content
                text_content = ""
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as temp_file:
                    download_txt_from_storage(file_data['file_id'], temp_file)
                    temp_file.seek(0)  # Go back to start of file
                    text_content = temp_file.read()
                
                # Extract references from text
                references = extract_references_from_text(text_content)
                
                # Save references to Firestore
                ref_batch = db.batch()
                for ref in references:
                    print(f"Reference: {ref}")
                    ref_doc = db.collection('references').document()
                    ref_batch.set(ref_doc, {
                        'full_reference_text': ref['reference_text'],
                        'authors': ref['authors'],
                        'title': ref['title'],
                        'year': ref['year'],
                        'source_file': file_data['file_id'],
                        'status': 'NewReference',
                        'depth': file_data.get('depth', 0) + 1,  # Increment depth from source paper
                        'created_timestamp': firestore.SERVER_TIMESTAMP,
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    })
                ref_batch.commit()
                
                # Update file status
                update_pdf_record(doc.id, {
                    'status': 'TextProcessed',
                    'reference_count': len(references),
                    'updated_timestamp': firestore.SERVER_TIMESTAMP
                })
                processed += 1
            except Exception as e:
                st.error(f"Error processing references for {file_data.get('file_id', 'unknown file')}: {str(e)}")
                # Update status to failed
                update_pdf_record(doc.id, {
                    'status': 'FailedProcessing',
                    'error_message': str(e),
                    'updated_timestamp': firestore.SERVER_TIMESTAMP
                })
                continue
            
        if processed > 0:
            st.success(f'Processed references from {processed} document(s).')
        else:
            st.info('No documents ready for reference processing.')

# Crawl References Section
st.divider()
col1, col2 = st.columns([1, 3])
with col1:
    crawl_limit = st.number_input('Number of references to crawl', min_value=1, value=1, step=1, key='crawl_limit')
with col2:
    if st.button('Crawl References'):
        with st.spinner('Crawling references...'):
            # Fetch NewReference records
            docs = db.collection('references').where('status', '==', 'NewReference').limit(crawl_limit).stream()
            processed = 0
        for doc in docs:
            try:
                reference_data = doc.to_dict()
                # Search for papers
                search_results = search_and_get_paper_links(reference_data['full_reference_text'], st.secrets['GOOGLE_API_KEY'], st.secrets['GOOGLE_CSE_ID'])
                
                downloaded_files = []
            except Exception as e:
                st.error(f"Error searching for reference {doc.id}: {str(e)}")
                # Update status to failed
                db.collection('references').document(doc.id).update({
                    'status': 'FailedProcessing',
                    'error_message': str(e),
                    'updated_timestamp': firestore.SERVER_TIMESTAMP
                })
                continue
            for result in search_results:
                url = result['url']
                title = result['title']
                
                # Check if URL was already processed
                existing_docs = db.collection('pdf_files').where('source_url', '==', url).limit(1).stream()
                if any(existing_docs):
                    st.info(f'PDF from {url} already exists in database, skipping...')
                    continue
                
                try:
                    # Download and save PDF with timeout
                    with st.spinner(f'Downloading PDF from {url}...'):
                        response = requests.get(url, timeout=120)  # 120 seconds timeout
                        if response.status_code == 200 and response.headers.get('content-type', '').lower() == 'application/pdf':
                            # Generate file ID from URL
                            file_id = f"{hashlib.md5(url.encode()).hexdigest()}.pdf"
                            
                            # Save to Firebase Storage
                            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                                temp_file.write(response.content)
                                temp_file.seek(0)
                                upload_pdf_to_storage(temp_file, file_id)
                            
                            # Add record to Firestore with source URL and title
                            doc_ref = db.collection('pdf_files').add({
                                'file_id': file_id,
                                'title': title,  # Add title from search results
                                'status': 'Initial',
                                'depth': reference_data.get('depth', 0) + 1,  # Use depth from reference
                                'source_url': url,
                                'source_reference': doc.id,  # Reference to the source reference document
                                'created_timestamp': firestore.SERVER_TIMESTAMP,
                                'updated_timestamp': firestore.SERVER_TIMESTAMP
                            })
                            
                            downloaded_files.append(file_id)
                            st.success(f'Successfully downloaded and saved PDF: {file_id}')
                except requests.Timeout:
                    st.error(f'Timeout downloading PDF from {url} after 120 seconds')
                    # Update reference record with timeout error
                    error_time = datetime.datetime.now().isoformat()
                    db.collection('references').document(doc.id).update({
                        'failed_downloads': firestore.ArrayUnion([{
                            'url': url,
                            'error': 'Download timeout after 120 seconds',
                            'timestamp': error_time
                        }]),
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    })
                    continue
                except Exception as e:
                    st.error(f'Error downloading PDF from {url}: {str(e)}')
                    # Update reference record with error
                    error_time = datetime.datetime.now().isoformat()
                    db.collection('references').document(doc.id).update({
                        'failed_downloads': firestore.ArrayUnion([{
                            'url': url,
                            'error': str(e),
                            'timestamp': error_time
                        }]),
                        'updated_timestamp': firestore.SERVER_TIMESTAMP
                    })
            
            # Update reference record
            db.collection('references').document(doc.id).update({
                'status': 'ProcessedReference',
                'search_results': search_results,
                'downloaded_files': downloaded_files,
                'updated_timestamp': firestore.SERVER_TIMESTAMP
            })
            processed += 1
        if processed > 0:
            st.success(f'Crawled {processed} reference(s).')
        else:
            st.info('No new references to crawl.')

st.divider()

