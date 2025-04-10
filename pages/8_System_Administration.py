import streamlit as st
from firebase_utils import add_missing_field

def main():
    st.title("System Administration")
    
    st.subheader("Database Management")
    
    if st.button("Add Triplet_GroupA"):
        add_missing_field('pdf_files', 'triplet_group_a', 'ToProcess')
        st.success("Successfully added 'triplet_group_a' field where missing")

if __name__ == "__main__":
    main()
