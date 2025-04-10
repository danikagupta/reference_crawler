from firebase_admin import credentials, firestore, initialize_app, storage, get_app

# Initialize Firebase only if it hasn't been initialized
def get_firebase_app():
    try:
        return get_app()
    except ValueError:
        # Initialize Firebase if not already initialized
        import streamlit as st
        
        # Get Firebase config from secrets
        firebase_config = dict(st.secrets['firebase'])
        
        # Create credentials from config
        cred = credentials.Certificate(firebase_config)
        return initialize_app(cred, {'storageBucket': 'referencecrawler.firebasestorage.app'})

# Get or initialize Firebase app
app = get_firebase_app()

# Get Firestore and Storage clients
db = firestore.client(app)
bucket = storage.bucket(app=app)

# Firebase utility functions
def upload_pdf_to_storage(file, filename):
    blob = bucket.blob(f'pdf_files/{filename}')
    blob.upload_from_file(file)
    return blob.public_url

def download_pdf_from_storage(filename, temp_file):
    blob = bucket.blob(f'pdf_files/{filename}')
    blob.download_to_filename(temp_file.name)

def download_txt_from_storage(filename, temp_file):
    """Download a text file from Firebase Storage"""
    blob = bucket.blob(f'txt_files/{filename}.txt')
    blob.download_to_filename(temp_file.name)

def upload_txt_to_storage(content, filename):
    blob = bucket.blob(f'txt_files/{filename}.txt')
    blob.upload_from_string(content)
    return blob.public_url

def add_pdf_record(file_id):
    db.collection('pdf_files').add({
        'file_id': file_id,
        'status': 'Initial',
        'depth': 1,
        'created_timestamp': firestore.SERVER_TIMESTAMP,
        'updated_timestamp': firestore.SERVER_TIMESTAMP,
        'triplet_group_a': 'ToProcess'
    })

def update_pdf_record(doc_id, updates):
    db.collection('pdf_files').document(doc_id).update(updates)

def download_text_from_storage(filename):
    """Download text content directly from Firebase Storage
    
    Args:
        filename (str): Name of the file (without .txt extension)
        
    Returns:
        str: Text content of the file
    """
    blob = bucket.blob(f'txt_files/{filename}.txt')
    return blob.download_as_text()

# Add more Firebase utility functions as needed
def add_missing_field(collection_name: str, field_name: str, default_value):
    """
    Adds a missing field with a default value to documents in a Firestore collection.

    Args:
        collection_name (str): The name of the Firestore collection.
        field_name (str): The name of the field to check/add.
        default_value: The value to assign if the field is missing.
    """
    docs = db.collection(collection_name).stream()

    for doc in docs:
        data = doc.to_dict()
        if field_name not in data:
            doc_ref = db.collection(collection_name).document(doc.id)
            doc_ref.update({field_name: default_value})
            print(f"Updated {doc.id}: set '{field_name}' to {default_value}")
        else:
            print(f"Skipped {doc.id}: '{field_name}' already exists")
