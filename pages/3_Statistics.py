import streamlit as st
from firebase_utils import db

st.set_page_config(
    page_title="Statistics",
    page_icon="📊",
)

st.title('📊 System Statistics')

# Get all files and references
files = list(db.collection('pdf_files').stream())
references = list(db.collection('references').stream())

# Count files by state, qualification, and depth
total_files = len(files)
files_by_state = {}
files_by_qualification = {'Qualified': 0, 'Not Qualified': 0, 'To Process': 0}
files_by_depth = {}
max_depth = 0

for file in files:
    data = file.to_dict()
    # Count by processing state
    state = data.get('status', 'Unknown')
    files_by_state[state] = files_by_state.get(state, 0) + 1
    
    # Count by qualification state
    if 'qualified' not in data:
        files_by_qualification['To Process'] += 1
    elif data['qualified']:
        files_by_qualification['Qualified'] += 1
    else:
        files_by_qualification['Not Qualified'] += 1

    # Count by depth
    depth = data.get('depth', 0)
    max_depth = max(max_depth, depth)
    files_by_depth[depth] = files_by_depth.get(depth, 0) + 1

# Count references by state
total_refs = len(references)
refs_by_state = {}
for ref in references:
    data = ref.to_dict()
    state = data.get('status', 'Unknown')
    refs_by_state[state] = refs_by_state.get(state, 0) + 1

# Display File Statistics
st.header('📄 Files in System')
st.metric('Total Files', total_files)

# Display depth statistics
if files_by_depth:
    st.subheader('Files by Depth')
    cols = st.columns(min(len(files_by_depth), 6))
    for i, (depth, count) in enumerate(sorted(files_by_depth.items())):
        with cols[i % len(cols)]:
            st.metric(f'Depth {depth}', count)

# Display qualification statistics
st.subheader('Files by Qualification')
cols = st.columns(3)
for i, (state, count) in enumerate(files_by_qualification.items()):
    with cols[i]:
        st.metric(state, count)

if files_by_state:
    st.subheader('Files by State')
    cols = st.columns(min(len(files_by_state), 4))
    for i, (state, count) in enumerate(files_by_state.items()):
        with cols[i % len(cols)]:
            st.metric(state, count)
else:
    st.info('No files in the system yet')

# Display Reference Statistics
st.header('🔗 References')
st.metric('Total References', total_refs)

if refs_by_state:
    st.subheader('References by State')
    cols = st.columns(min(len(refs_by_state), 4))
    for i, (state, count) in enumerate(refs_by_state.items()):
        with cols[i % len(cols)]:
            st.metric(state, count)
else:
    st.info('No references in the system yet')

# Show recent activity
if files:
    st.header('📅 Recent Activity')
    
    # Sort files by timestamp if available
    recent_files = sorted(
        [f for f in files if f.to_dict().get('updated_timestamp')],
        key=lambda x: x.to_dict().get('updated_timestamp', 0),
        reverse=True
    )[:5]

    if recent_files:
        st.subheader('Latest Files')
        for file in recent_files:
            data = file.to_dict()
            st.markdown(f"**{data.get('file_id', 'Unknown')}** - Status: {data.get('status', 'Unknown')}")

    # Sort references by timestamp if available
    recent_refs = sorted(
        [r for r in references if r.to_dict().get('updated_timestamp')],
        key=lambda x: x.to_dict().get('updated_timestamp', 0),
        reverse=True
    )[:5]

    if recent_refs:
        st.subheader('Latest References')
        for ref in recent_refs:
            data = ref.to_dict()
            st.markdown(f"**{data.get('title', 'Unknown Title')}** - Status: {data.get('status', 'Unknown')}")
