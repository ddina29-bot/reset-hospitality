import streamlit as st
from supabase import create_client, Client

# --- 1. CONNECTION ---
URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs"
supabase: Client = create_client(URL, KEY)

# Memory for Filter to prevent "jumping"
if 'filter_choice' not in st.session_state:
    st.session_state.filter_choice = 'All'

# --- 2. DATABASE FUNCTIONS ---
def update_status(suite_id, new_status):
    supabase.table("suites").update({"status": new_status}).eq("id", suite_id).execute()
    st.rerun()

# --- 3. UI: HEADER ---
st.title("👋 Welcome back, Dina")
st.write("Reset Hospitality Studio | Management Dashboard")

# --- 4. FETCH DATA ---
try:
    response = supabase.table("suites").select("*").order("name").execute()
    suites = response.data
except Exception as e:
    st.error(f"Connection Error: {e}")
    suites = []

# --- 5. PHASE METRICS ---
ready = len([s for s in suites if s.get('status') == 'Ready'])
in_progress = len([s for s in suites if s.get('status') == 'In Progress'])
completed = len([s for s in suites if s.get('status') == 'Completed'])

col1, col2, col3 = st.columns(3)
col1.metric("Apartments Ready", ready)
col2.metric("In Progress", in_progress)
col3.metric("Completed", completed)

st.divider()

# --- 6. FILTER & SEARCH ---
search = st.text_input("🔍 Search Properties", placeholder="Enter suite number...")

st.session_state.filter_choice = st.selectbox(
    "🎯 Filter by Status", 
    ["All", "Ready", "In Progress", "Completed", "Maintenance"],
    index=["All", "Ready", "In Progress", "Completed", "Maintenance"].index(st.session_state.filter_choice)
)

# --- 7. THE PROPERTY LIST ---
if not suites:
    st.info("Your list is empty. Please add suites in Supabase or check your RLS policies.")
else:
    for suite in suites:
        # Filter Logic
        if st.session_state.filter_choice != "All" and suite['status'] != st.session_state.filter_choice:
            continue
        if search.lower() not in suite['name'].lower():
            continue

        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader(f"SUITE {suite['name']}")
                st.write(f"Current Phase: **{suite['status']}**")
                
                # Special Requests Area
                notes = st.text_area("Special Requests", value=suite.get('notes', ""), key=f"n_{suite['id']}")
                if notes != suite.get('notes'):
                    supabase.table("suites").update({"notes": notes}).eq("id", suite['id']).execute()

            with c2:
                # Working Buttons
                if st.button("🚀 Start", key=f"s_{suite['id']}"):
                    update_status(suite['id'], "In Progress")
                if st.button("✅ Done", key=f"d_{suite['id']}"):
                    update_status(suite['id'], "Completed")
                if st.button("🔧 Maint.", key=f"m_{suite['id']}"):
                    update_status(suite['id'], "Maintenance")

# --- 8. MANAGEMENT SIDEBAR ---
with st.sidebar:
    st.header("Management Tools")
    if st.button("📊 Generate Report"):
        st.write("Exporting data...")
        st.download_button("Download CSV", "Suite,Status\n101,Completed", "report.csv")
