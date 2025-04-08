import streamlit as st
import tempfile
from main import extract_text_from_pdf

st.set_page_config(
    page_title="Debug Tools",
    page_icon="🔧",
    layout="wide"
)

st.title('🔧 Debugging Tools')

st.header("PDF Text Extraction Debugger")
st.write("Upload a PDF file to see the extracted text without saving to Firebase.")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

if uploaded_file:
    st.write("File uploaded:", uploaded_file.name)
    
    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name
        
        try:
            # Extract text using the same function as in Processing
            with st.spinner('Extracting text from PDF...'):
                extracted_text = extract_text_from_pdf(temp_file_path)
                
                # Show results in expanders
                with st.expander("📄 Extracted Text", expanded=True):
                    st.text_area("Full Text Content", 
                               value=extracted_text,
                               height=400)
                    
                # Show text statistics
                with st.expander("📊 Text Statistics"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Characters", len(extracted_text))
                    with col2:
                        st.metric("Total Words", len(extracted_text.split()))
                    with col3:
                        st.metric("Total Lines", len(extracted_text.splitlines()))
                    
                    # Show first few characters of each page if text is very long
                    if len(extracted_text) > 1000:
                        st.subheader("Text Preview by Section")
                        sections = extracted_text.split('\n\n')
                        for i, section in enumerate(sections[:5]):  # Show first 5 sections
                            with st.expander(f"Section {i+1}"):
                                st.text(section[:200] + "..." if len(section) > 200 else section)
                        
                        if len(sections) > 5:
                            st.info(f"{len(sections)-5} more sections not shown")
                
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
else:
    st.info("Please upload a PDF file to begin debugging.")
