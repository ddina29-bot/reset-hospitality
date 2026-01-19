import streamlit as st
from supabase import create_client, Client

# --- 1. CONNECTION ---
URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs"
supabase: Client = create_client(URL, KEY)

# Memory for Filter and Navigation
if 'filter_choice' not in st.session_state:
    st.session_state.filter_choice = 'All'
if 'view' not in st.session_state:
    st.session_state.view = 'Dashboard'

# --- 2. DATABASE FUNCTIONS (Safety First) ---
def update_db(suite_id, updates):
    try:
        supabase.table("suites").update(updates).eq("id", suite_id).execute()
        st.rerun()
    except Exception as e:
        st.error(f"Save failed. Make sure your SQL columns match: {e}")

def add_suite(name):
    try:
        supabase.table("suites").insert({"name": name, "status": "Ready"}).execute()
        st.rerun()
    except Exception as e:
        st.error(f"Could not add suite. Check your SQL 'suites' table: {e}")

# --- 3. FETCH DATA ---
try:
    response = supabase.table("suites").select("*").execute()
    suites = response.data if response.data else []
except:
    suites = []
    st.error("Cannot connect to your SQL table 'suites'.")

# --- 4. TOP HEADER & WELCOME ---
st.title("👋 Welcome to Suite Manager")
st.write("Phase 1-4: Complete Property Overview")

# Calculate categories from your data
ready = len([s for s in suites if str(s.get('status')).lower() == 'ready'])
progress = len([s for s in suites if str(s.get('status')).lower() == 'in progress'])
completed = len([s for s in suites if str(s.get('status')).lower() == 'completed'])
maint = len([s for s in suites if str(s.get('status')).lower() == 'maintenance'])

# The 4 Main Status Columns (Restored)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Apartments Ready", ready)
col2.metric("In Progress", progress)
col3.metric("Completed", completed)
col4.metric("Maintenance", maint)

st.divider()

# --- 5. SIDEBAR / MANAGEMENT ---
with st.sidebar:
    st.header("Management Tools")
    if st.button("📊 Reports"): st.session_state.view = 'Reports'
    if st.button("🏠 Dashboard"): st.session_state.view = 'Dashboard'
    
    st.divider()
    st.subheader("Add New Property")
    new_name = st.text_input("Suite Name")
    if st.button("➕ Add to List"):
        add_suite(new_name)

# --- 6. DASHBOARD LOGIC ---
if st.session_state.view == 'Dashboard':
    search = st.text_input("🔍 Search (Suite # or Special Request)", placeholder="Type here...")
    
    st.session_state.filter_choice = st.selectbox(
        "🎯 Filter by Status", 
        ["All", "Ready", "In Progress", "Completed", "Maintenance"],
        index=["All", "Ready", "In Progress", "Completed", "Maintenance"].index(st.session_state.filter_choice)
    )

    for suite in suites:
        s_status = suite.get('status', 'Ready')
        s_name = suite.get('name', 'Unknown')
        s_req = suite.get('special_requests', '') # Restore Special Requests

        # Filtering logic
        if st.session_state.filter_choice != "All" and s_status != st.session_state.filter_choice:
            continue
        if search.lower() not in s_name.lower() and search.lower() not in str(s_req).lower():
            continue

        with st.container(border=True):
            head, btns = st.columns([3, 2])
            with head:
                st.subheader(f"**{s_name}**")
                st.write(f"Current Status: **{s_status}**")
                
                # RESTORED: Special Requests Box
                new_req = st.text_area("Special Requests / Notes", value=s_req, key=f"req_{suite['id']}")
                if new_req != s_req:
                    update_db(suite['id'], {"special_requests": new_req})

            with btns:
                st.write("Update Status:")
                if st.button("🚀 Start", key=f"p_{suite['id']}"): update_db(suite['id'], {"status": "In Progress"})
                if st.button("✅ Done", key=f"d_{suite['id']}"): update_db(suite['id'], {"status": "Completed"})
                if st.button("🔧 Maint.", key=f"m_{suite['id']}"): update_db(suite['id'], {"status": "Maintenance"})

elif st.session_state.view == 'Reports':
    st.header("Property Progress Report")
    if suites:
        st.table(suites)
    else:
        st.write("No data available for reports.")
