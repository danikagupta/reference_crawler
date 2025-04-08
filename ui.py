import streamlit as st

st.set_page_config(
    page_title="Reference Crawler",
    page_icon="📚",
)

st.title('📚 Reference Crawler System')

st.markdown("""
## Welcome to Reference Crawler!

This application helps you analyze academic papers and track their references. Here's what you can do:

### 🔍 Main Features:

1. **Upload Papers** (Page 2)
   - Upload PDF files of academic papers
   - Files are securely stored in Firebase

2. **Process Papers** (Page 3)
   - Extract text from PDFs
   - Identify and extract references
   - Crawl referenced papers

3. **View Statistics** (Page 4)
   - Track processing status
   - View paper statistics
   - Monitor reference chains

4. **Download Data** (Page 5)
   - Export processed data
   - Download reference networks

### 📝 Getting Started:

1. Navigate to the "Upload" page
2. Upload your academic paper (PDF)
3. Go to "Processing" to extract and analyze references
4. Check "Statistics" to monitor progress
5. Use "Download" to export your data

### 🔧 Need Help?

Check out our documentation or contact support if you need assistance.
""")