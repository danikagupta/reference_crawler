# Product Requirements Document (PRD)

## Reference Crawler System

### Overview
The Reference Crawler system is designed to process PDF files, extract references, and manage data using a Streamlit UI. The system will store information in Firebase and Firestore.

### Key Requirements
1. **Technology Stack**:
   - Python for backend processing.
   - Streamlit for the user interface.
   - Firebase for file storage.
   - Firestore for database management.

2. **Initial Setup**:
   - Upload a small number of PDF files.
   - Store files in Firebase and create records in Firestore with status "Initial" and Depth=1.

3. **UI Components**:
   - **Process PDF Button**: Processes PDFs marked as "Initial", extracts text, and updates records.
   - **Extract References Button**: Extracts references from TXT files and updates records.
   - **Crawl Reference Button**: Searches for references using Tavily API and updates records.
   - **Download Data Buttons**: Allows users to download data from tables.

4. **Error Handling**:
   - Update records with error statuses and reasons if processing fails.

5. **Data Management**:
   - Maintain accurate records in Firestore with status updates and error reasons.

### Next Steps
- Review and approve this PRD.
- Create a detailed Engineering plan based on the approved PRD.
