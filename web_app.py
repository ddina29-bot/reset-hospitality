import streamlit as st
from supabase import create_client, Client

# 1. Database Connection
# Replace these with your actual Supabase credentials
URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs"
supabase: Client = create_client(URL, KEY)

# 2. Memory Management (Session State)
# This prevents the filter from resetting to "All" when you click a button
if 'filter_choice' not in st.session_state:
    st.session_state.filter_choice = 'All'

# 3. Helper Functions
def update_suite_data(suite_id, updates):
    """Sends any change (status or instructions) to Supabase"""
    supabase.table("suites").update(updates).eq("id", suite_id).execute()
    st.rerun()

# 4. Fetch Live Data
# We pull the data every time the app runs to keep counters accurate
response = supabase.table("suites").select("*").order("name").execute()
suites = response.data

# 5. Dynamic Counters
# These calculate automatically based on the 'status' column in your DB
total_count = len(suites)
done_count = len([s for s in suites if s['status'] == 'Completed'])
maint_count = len([s for s in suites if s['status'] == 'Maintenance'])

# --- UI LAYOUT ---

# Top Statistics Row
col1, col2, col3 = st.columns(3)
col1.metric("Total", total_count)
col2.metric("Done", done_count)
col3.metric("Maint.", maint_count)

st.divider()

# Search and Filter Section
search_query = st.text_input("🔍 Search Suites", placeholder="Enter suite name...")

# The "Memory" Filter - it stays on your choice even after a click
st.session_state.filter_choice = st.selectbox(
    "🎯 Filter by Status", 
    ["All", "Completed", "Maintenance"],
    index=["All", "Completed", "Maintenance"].index(st.session_state.filter_choice)
)

st.write("---")

# 6. The Main List
for suite in suites:
    # Filter Logic: Skip suites that don't match the search or the dropdown
    if st.session_state.filter_choice != "All" and suite['status'] != st.session_state.filter_choice:
        continue
    if search_query.lower() not in suite['name'].lower():
        continue

    # Card Display
    with st.container(border=True):
        header_col, btn_col = st.columns([3, 1])
        
        with header_col:
            st.subheader(f"**{suite['name']}**")
            # Color coding the status text
            status_color = "green" if suite['status'] == "Completed" else "red"
            st.markdown(f"Status: :{status_color}[{suite['status']}]")
        
        with btn_col:
            # When clicked, this updates the DB and the counters update automatically
            if st.button("🔧 MAINT", key=f"btn_{suite['id']}"):
                update_suite_data(suite['id'], {"status": "Maintenance"})

        # Special Instructions Box
        # This saves to the database as soon as you click 'Enter' or click away
        current_instr = suite.get('instructions', "")
        new_instr = st.text_area(
            "Special Instructions", 
            value=current_instr, 
            key=f"text_{suite['id']}",
            height=68
        )
        
        # Save instruction changes if they are different from what's in the DB
        if new_instr != current_instr:
            update_suite_data(suite['id'], {"instructions": new_instr})
