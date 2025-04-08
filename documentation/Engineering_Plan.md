# Engineering Plan

## Reference Crawler System

### Overview
This document outlines the technical implementation plan for the Reference Crawler system, detailing the architecture, components, and development phases.

### Architecture
- **Backend**: Python
- **Frontend**: Streamlit UI
- **Database**: Firebase for file storage, Firestore for data management

### Components
1. **File Upload**
   - Implement functionality to upload PDF files to Firebase.
   - Create Firestore records with status "Initial" and Depth=1.

2. **Process PDF**
   - Develop a function to extract text from PDF files.
   - Update Firestore records with TXT file location and status "TxtGenerated".
   - Handle errors and update records with status "TxtNotGenerated".

3. **Extract References**
   - Implement LLM integration to extract references from TXT files.
   - Update Firestore records with status "RefExtracted".
   - Handle errors and update records with status "RefNotExtracted".

4. **Crawl References**
   - Use Tavily API to search and download papers.
   - Update Firestore records with status "ProcessedReference".
   - Handle errors and update records with status "ErrorProcessingReference".

5. **Download Data**
   - Implement functionality to download data from Firestore tables.

### Database Schema
- **PDF Files Collection**:
  - `file_id`: Unique identifier for each PDF file.
  - `status`: Current processing status (e.g., Initial, TxtGenerated, RefExtracted).
  - `depth`: Integer indicating the depth of processing.
  - `created_timestamp`: Timestamp when the record was created.
  - `updated_timestamp`: Timestamp when the record was last updated.
  - `txt_file_location`: Location of the extracted TXT file.
  - `pdf_filename`: Complete filename for the PDF file.
  - `txt_filename`: Complete filename for the TXT file.
  - `authors`: Names of the authors.
  - `title`: Title of the document.
  - `year_of_publication`: Year the document was published.
  - `full_citation`: Full citation record.
  - `reason`: Error reason if processing fails.

- **References Collection**:
  - `reference_id`: Unique identifier for each reference.
  - `source_file_id`: ID of the source PDF file.
  - `status`: Current processing status (e.g., NewReference, ProcessedReference).
  - `depth`: Integer indicating the depth of the reference.
  - `created_timestamp`: Timestamp when the record was created.
  - `updated_timestamp`: Timestamp when the record was last updated.
  - `authors`: Names of the authors.
  - `title`: Title of the reference.
  - `year_of_publication`: Year the reference was published.
  - `full_citation`: Full citation record.
  - `reason`: Error reason if processing fails.

### Filesystem Directory Structure
- **/pdf_files/**: Directory to store uploaded PDF files.
- **/txt_files/**: Directory to store extracted TXT files.

### Langchain and Tavily Integration
- **Langchain**:
  - Utilize Langchain for PDF text extraction and reference extraction.
  - Modular design allows easy integration and expansion of language models.

- **Tavily API**:
  - Implement an abstraction layer for Tavily API to facilitate future migration to other search providers.
  - Ensure the system is flexible enough to switch APIs without major code changes.

### Migration Considerations
- Design the system with modularity in mind, allowing components to be swapped or upgraded independently.
- Maintain clear documentation on API integration points to streamline future migrations or integrations.
- Regularly review and update dependencies to ensure compatibility with the latest versions of Langchain and any other libraries used.

### Development Phases
1. **Phase 1**: Setup Firebase and Firestore
2. **Phase 2**: Develop File Upload and Process PDF functionalities
3. **Phase 3**: Implement Extract References and Crawl References functionalities
4. **Phase 4**: Finalize UI and integrate all components
5. **Phase 5**: Testing and Deployment

### Next Steps
- Begin development as per the phases outlined above.
