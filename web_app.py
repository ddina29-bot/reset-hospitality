import streamlit as st
from supabase import create_client, Client

# --- 1. Database Setup ---
SUPABASE_URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs" # Ensure your long key is pasted here
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. Luxury Branding ---
st.set_page_config(page_title="RE-SET Hospitality", layout="centered")
GOLD = "#D4AF37"

st.markdown(f"<h1 style='text-align: center;'>RE-SET</h1><h3 style='text-align: center; color: {GOLD};'>Hospitality Studio</h3><hr>", unsafe_allow_html=True)

# --- 3. Login Logic ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("LOG IN"):
        # Temporary bypass for testing
        if email == "dina@test.com" and password == "123456":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied")
else:
    # --- 4. Live Dashboard & Metrics ---
    st.subheader("PROPERTY OVERVIEW")
    
    try:
        response = supabase.table("properties").select("id, name, status").execute()
        properties = response.data
        
        total_rooms = len(properties)
        completed_rooms = sum(1 for p in properties if p['status'] == 'Completed')
        remaining = total_rooms - completed_rooms

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Properties", total_rooms)
        col_b.metric("Done", completed_rooms)
        col_c.metric("Remaining", remaining)
        st.markdown("---")

        # --- 5. Search & Filter Bar ---
        search_query = st.text_input("🔍 Search by Property Name", "").strip().lower()
        status_filter = st.selectbox("🎯 Filter by Status", ["All", "Ready", "In Progress", "Completed"])

        filtered_properties = [
            p for p in properties 
            if (search_query in p['name'].lower()) and 
               (status_filter == "All" or p['status'] == status_filter)
        ]

        # --- 6. Property List ---
        if not filtered_properties:
            st.info("No properties match your search.")
        else:
            for item in filtered_properties:
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{item['name'].upper()}**")
                        status = item.get('status', 'Ready')
                        color = "#27AE60" if status == "Completed" else "#D4AF37"
                        st.markdown(f"<span style='color:{color}'>Status: {status}</span>", unsafe_allow_html=True)
                    with col2:
                        if "Progres" in status:
                            if st.button("MARK FINISHED", key=item['id']):
                                supabase.table("properties").update({"status": "Completed"}).eq("id", item['id']).execute()
                                st.rerun()
                        elif status == "Completed":
                            st.button("SERVICE DONE", disabled=True, key=item['id'])
                        else:
                            if st.button("START SERVICE", key=item['id']):
                                supabase.table("properties").update({"status": "In Progress"}).eq("id", item['id']).execute()
                                st.rerun()

        # --- 7. Manager Automation ---
        st.markdown("---")
        st.subheader("MANAGER AUTOMATION")
        if st.button("🔄 RESET ALL FOR TOMORROW", use_container_width=True):
            supabase.table("properties").update({"status": "Ready"}).neq("name", "VOID").execute()
            st.success("All rooms reset to Ready.")
            st.rerun()

    except Exception as e:
        st.error(f"Database Error: {e}")

    # Center the Log Out button at the bottom
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

