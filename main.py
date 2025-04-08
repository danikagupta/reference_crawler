import streamlit as st

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]="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"
os.environ["LANGSMITH_API_KEY"]="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"
os.environ["LANGCHAIN_PROJECT"]="ReferenceCrawler"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"

# Initialize Langchain components
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
llm = ChatOpenAI(model=st.secrets['OPENAI_API_MODEL'], api_key=st.secrets['OPENAI_API_KEY'])

class ReferenceResult:
    reference_text : str
    authors: str
    title: str
    year: str

class ReferenceResults:
    references : list[ReferenceResult]


# Core processing functions
def extract_text_from_pdf(file_path):
    """Extract text from PDF and return as a single string"""
    # Load PDF
    loader = PyPDFLoader(file_path)
    # Load the document pages
    pages = loader.load()
    # Combine all page content
    text = "\n\n".join(page.page_content for page in pages)
    return text

def extract_references_from_text(text : str):
    """Extract references from text using LLM"""
    if (len(text)>50000):
        text=text[:50000]

    prompt = f"""
    Extract all academic references from the following text. 
    Format each reference as a separate item in a list with the following fields: reference_text, authors, title, year.   
    If no references are found, return an empty list.
    Please double-check your work and ensure that every single reference is correctly extracted.
    Call the list "references"
    \n\nText:\n {text}
    """

    response=llm.with_structured_output(ReferenceResults).invoke(
        [SystemMessage(content=prompt)]
    )
    print(f"Response: {response}")
    return response['references']

# Function to search and download papers
def search_and_download(query,api_key):
    search_provider = SearchProvider(api_key=api_key)
    results = search_provider.search_paper(query)
    # Process results
    return results
