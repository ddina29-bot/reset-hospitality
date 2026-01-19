import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# --- 1. Database Setup ---
SUPABASE_URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs" # Replace with your long key
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
        if email == "dina@test.com" and password == "123456":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied")
else:
    # --- 4. Dashboard & Automated Metrics ---
    st.subheader("PROPERTY OVERVIEW")
    try:
        response = supabase.table("properties").select("*").execute()
        properties = response.data
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total", len(properties))
        col_b.metric("Done", sum(1 for p in properties if p['status'] == 'Completed'))
        col_c.metric("Remaining", sum(1 for p in properties if p['status'] != 'Completed'))
        st.markdown("---")

        # --- 5. Search & Filter Bar ---
        search_query = st.text_input("🔍 Search Properties", "").strip().lower()
        status_filter = st.selectbox("🎯 Filter", ["All", "Ready", "In Progress", "Completed"], index=1)

        filtered = [p for p in properties if (search_query in p['name'].lower()) and (status_filter == "All" or p['status'] == status_filter)]

        # --- 6. Property List & Timestamp Logic ---
        if not filtered:
            st.info("No properties match your filter.")
        else:
            for item in filtered:
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**{item['name'].upper()}**")
                        color = "#27AE60" if item['status'] == "Completed" else "#D4AF37"
                        st.markdown(f"<span style='color:{color}'>Status: {item['status']}</span>", unsafe_allow_html=True)
                        if item.get('last_completed_at'):
                            # Showing the time it was finished
                            st.caption(f"Finished at: {item['last_completed_at'][:16].replace('T', ' ')}")

                    with c2:
                        if item['status'] == "In Progress":
                            if st.button("MARK FINISHED", key=item['id']):
                                # This update now saves the EXACT time
                                now = datetime.now().isoformat()
                                supabase.table("properties").update({"status": "Completed", "last_completed_at": now}).eq("id", item['id']).execute()
                                st.rerun()
                        elif item['status'] == "Completed":
                            st.button("SERVICE DONE", disabled=True, key=item['id'])
                        else:
                            if st.button("START SERVICE", key=item['id']):
                                supabase.table("properties").update({"status": "In Progress"}).eq("id", item['id']).execute()
                                st.rerun()

        # --- 7. Manager Controls ---
        st.markdown("---")
        if st.button("🔄 RESET ALL FOR TOMORROW"):
            # Clear status AND the timestamp for the new day
            supabase.table("properties").update({"status": "Ready", "last_completed_at": None}).neq("name", "VOID").execute()
            st.success("Board cleared and timestamps reset.")
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
