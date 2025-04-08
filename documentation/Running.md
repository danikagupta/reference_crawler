# Running the Reference Crawler System

This document provides instructions on setting up and running the Reference Crawler system, including configuration of Firebase credentials and datastore.

## Prerequisites
- Python 3.7+
- Firebase account with Firestore and Storage enabled
- Required Python packages:
  - `streamlit`: Web interface
  - `pandas`: Data manipulation and display
  - `firebase-admin`: Firebase integration
  - `langchain` and `langchain-openai`: Text processing
  - `pypdf`: PDF processing
  - `tavily-python`: Reference searching
- API Keys:
  - OpenAI API key for reference extraction
  - Tavily API key for reference crawling

## Setting Up Firebase
1. **Create a Firebase Project**:
   - Go to the [Firebase Console](https://console.firebase.google.com/).
   - Click on 'Add Project' and follow the instructions to create a new project.

2. **Enable Firestore and Storage**:
   - In your Firebase project, navigate to 'Firestore Database' and click 'Create Database'.
   - Navigate to 'Storage' and click 'Get Started' to enable Firebase Storage.

3. **Generate Firebase Credentials**:
   - Go to 'Project Settings' in the Firebase Console.
   - Under 'Service accounts', click 'Generate new private key' to download the credentials file.
   - Save the JSON file to your project directory.

4. **Update Firebase Configuration**:
   - In `firebase_utils.py`, update the path to your Firebase credentials file:
     ```python
     cred = credentials.Certificate('path/to/your/credentials.json')
     ```
   - Update the storage bucket name:
     ```python
     initialize_app(cred, {'storageBucket': 'your-bucket-name.appspot.com'})
     ```

## Setting Up API Keys
1. **Configure OpenAI API**:
   - Get your OpenAI API key from [OpenAI's website](https://platform.openai.com/)
   - Add it to `.streamlit/secrets.toml`:
     ```toml
     OPENAI_API_KEY = "your-openai-api-key"
     OPENAI_API_MODEL = "gpt-4" # or your preferred model
     ```

2. **Configure Tavily API**:
   - Get your Tavily API key from [Tavily's website](https://tavily.com)
   - Add it to `.streamlit/secrets.toml`:
     ```toml
     TAVILY_API_KEY = "your-tavily-api-key"
     ```

## Running the Application
1. **Start the Streamlit App**:
   - Navigate to the project directory in your terminal.
   - Run the following command to start the Streamlit app:
     ```bash
     streamlit run ui.py
     ```

2. **Using the Multi-Page Interface**:
   - **Home Page**: Overview and system status
   - **Processing Page**: Process files through four stages:
     1. Text Extraction: Convert PDFs to text
     2. Paper Qualification: Evaluate papers for relevance
     3. Reference Processing: Extract references from text
     4. Reference Crawling: Search for referenced papers
   - **Upload Page**: Upload new PDFs to the system
   - **Search Page**: Search through processed references
   - **View Page**: View and download files and references
     - Files table with status filtering and search
     - References table with multiple filter options
     - Download PDFs and extracted text files
   - **Edit Page**: Directly edit database records
     - Edit PDF Files:
       - Update status (Initial, TextExtracted, TextProcessed)
       - Modify depth and reference count
       - All changes are timestamped
     - Edit References:
       - Update status (NewReference, ProcessedReference)
       - Modify reference text, authors, title, and year
       - Changes are tracked with timestamps
   - **Debug Page**: Tools for testing and debugging
     - PDF Text Extraction:
       - Upload and process PDFs without saving to database
       - View extracted text and statistics
       - Section-by-section text preview
       - Character, word, and line counts
   - **Download Page**: Export processed data

## Processing Flow and Storage Structure

### Firebase Storage Organization
- `/pdf_files/`: Original uploaded PDF documents
- `/txt_files/`: Extracted text content from PDFs

### Processing Stages
1. **Text Extraction Stage**:
   - Reads PDF files from Firebase Storage
   - Extracts text content using PyPDF
   - Saves extracted text back to storage
   - Updates status to "TextExtracted"

2. **Paper Qualification Stage**:
   - Evaluates unqualified papers with status 'TextExtracted' or 'TextProcessed'
   - Uses GPT-4 to assess relevance to consumer behavior and persuasion topics:
     - Consumer decision making
     - Persuasion techniques
     - Marketing influence
     - Social media influence
     - Behavioral economics
     - Consumer psychology
   - Analyzes paper content with structured output:
     - Relevance assessment
     - Topics found
     - Confidence score
     - Reasoning for decision
   - Sets 'qualified' field in database (true if relevant with high confidence)
   - Skips papers that have already been qualified
   - Papers can be qualified at any point after text extraction

3. **Reference Processing Stage**:
   - User selects number of files to process in this batch
   - Takes files that are:
     - Marked as qualified (qualified = true)
     - Have status "TextExtracted"
     - Up to the specified limit
   - Loads extracted text from `/txt_files/{file_id}.txt`
   - Uses OpenAI to identify references in the text
   - Creates structured reference records in Firestore with:
     - Full reference text
     - Authors
     - Title
     - Year
   - Updates file status to "TextProcessed"
   - Stores reference count in file record

3. **Reference Crawling Stage**:
   - User selects number of references to crawl in this batch
   - Takes references with status "NewReference" (up to the specified limit)
   - Uses Google Custom Search API to find PDF links
   - For each search result:
     - Checks if PDF URL already exists in database to avoid duplicates
     - Downloads PDF if new and stores in Firebase Storage
     - Creates new PDF file record with:
       - Unique file_id (based on URL hash)
       - Title from search results
       - Status: "Initial"
       - Incremented depth (parent depth + 1)
       - Source URL and reference document ID
   - Updates reference record with:
     - Status: "ProcessedReference"
     - Search results list
     - List of downloaded file IDs
     - Updated timestamp

### File Status Progression
- PDF Files: Initial → TextExtracted → TextProcessed
- References: NewReference → ProcessedReference

## Troubleshooting
- Ensure your Firebase credentials file is correctly referenced in `firebase_utils.py`
- Check that Firestore and Storage are properly set up and permissions are configured
- Verify that all required Python packages are installed
- Confirm API keys are correctly set in `.streamlit/secrets.toml`
- Check Firebase Storage permissions if file uploads fail
- Monitor Firestore quotas and limits

For further assistance, refer to:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Tavily API Documentation](https://docs.tavily.com)
