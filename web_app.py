import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- 1. CONNECTION & SETUP ---
URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs"
supabase: Client = create_client(URL, KEY)

# Memory for Filter and Navigation
if 'filter_choice' not in st.session_state:
    st.session_state.filter_choice = 'All'
if 'view' not in st.session_state:
    st.session_state.view = 'Dashboard'

# --- 2. DATABASE FUNCTIONS ---
def update_db(suite_id, updates):
    supabase.table("suites").update(updates).eq("id", suite_id).execute()
    st.rerun()

def add_suite(name):
    supabase.table("suites").insert({"name": name, "status": "Ready"}).execute()
    st.rerun()

# --- 3. FETCH DATA ---
response = supabase.table("suites").select("*").order("name").execute()
suites = response.data

# --- 4. SIDEBAR (Management & Reports) ---
with st.sidebar:
    st.title("Settings & Management")
    if st.button("📊 View Reports"):
        st.session_state.view = 'Reports'
    if st.button("🏠 Back to Dashboard"):
        st.session_state.view = 'Dashboard'
    
    st.divider()
    with st.expander("➕ Add New Suite"):
        new_name = st.text_input("Suite Name")
        if st.button("Save New Suite"):
            add_suite(new_name)

# --- 5. TOP HEADER & WELCOME ---
st.title("👋 Welcome to Suite Manager")
st.write("Current Shift Status and Property Overview")

# Calculate specific categories
ready = len([s for s in suites if s['status'] == 'Ready'])
in_progress = len([s for s in suites if s['status'] == 'In Progress'])
completed = len([s for s in suites if s['status'] == 'Completed'])
maint = len([s for s in suites if s['status'] == 'Maintenance'])

# Visual Stats Bar
col1, col2, col3, col4 = st.columns(4)
col1.metric("Apartments Ready", ready)
col2.metric("In Progress", in_progress)
col3.metric("Completed", completed)
col4.metric("Maintenance", maint)

st.divider()

# --- 6. VIEW LOGIC (Dashboard vs Reports) ---
if st.session_state.view == 'Reports':
    st.subheader("Property Reports")
    df = pd.DataFrame(suites)
    st.dataframe(df) # Shows the full SQL table as a report
    if st.button("Export to CSV"):
        st.write("Download link generated...")

else:
    # --- DASHBOARD VIEW ---
    search = st.text_input("🔍 Search Suites", placeholder="Search names or requests...")
    
    st.session_state.filter_choice = st.selectbox(
        "Filter by Status", 
        ["All", "Ready", "In Progress", "Completed", "Maintenance"],
        index=["All", "Ready", "In Progress", "Completed", "Maintenance"].index(st.session_state.filter_choice)
    )

    for suite in suites:
        # Filter Logic
        if st.session_state.filter_choice != "All" and suite['status'] != st.session_state.filter_choice:
            continue
        if search.lower() not in suite['name'].lower() and search.lower() not in str(suite.get('special_requests', '')).lower():
            continue

        with st.container(border=True):
            c1, c2 = st.columns([3, 2])
            with c1:
                st.subheader(suite['name'])
                st.write(f"Status: **{suite['status']}**")
                # Special Requests/Instructions
                req = st.text_area("Special Requests", value=suite.get('special_requests', ""), key=f"req_{suite['id']}")
                if req != suite.get('special_requests'):
                    update_db(suite['id'], {"special_requests": req})

            with c2:
                st.write("Change Status:")
                # Quick Action Buttons
                if st.button("🚀 Start", key=f"prog_{suite['id']}"):
                    update_db(suite['id'], {"status": "In Progress"})
                if st.button("✅ Complete", key=f"comp_{suite['id']}"):
                    update_db(suite['id'], {"status": "Completed"})
                if st.button("🔧 Maint.", key=f"maint_{suite['id']}"):
                    update_db(suite['id'], {"status": "Maintenance"})
