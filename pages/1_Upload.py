import streamlit as st
from firebase_utils import upload_pdf_to_storage, add_pdf_record

st.set_page_config(
    page_title="Upload Papers",
    page_icon="📄",
)

st.title('📄 Upload Papers')

st.markdown("""
Upload your academic papers here. The system accepts PDF files and stores them securely in Firebase.
""")

# File Upload
uploaded_file = st.file_uploader('Upload PDF', type='pdf')
if uploaded_file is not None:
    with st.spinner('Uploading file...'):
        # Save file to Firebase Storage
        file_url = upload_pdf_to_storage(uploaded_file, uploaded_file.name)
        # Create Firestore record
        add_pdf_record(uploaded_file.name)
        st.success(f'File {uploaded_file.name} uploaded successfully.')
        st.markdown(f"**Next Steps:**\n1. Go to the Processing page to extract references\n2. Monitor progress in Statistics")
