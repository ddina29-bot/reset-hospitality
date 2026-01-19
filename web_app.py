import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# --- 1. Database Setup ---
SUPABASE_URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs" # Paste your key here
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. Luxury Branding ---
st.set_page_config(page_title="RE-SET Hospitality", layout="centered")
GOLD = "#D4AF37"
st.markdown(f"<h1 style='text-align: center;'>RE-SET</h1><h3 style='text-align: center; color: {GOLD};'>Hospitality Studio</h3><hr>", unsafe_allow_html=True)

# --- 3. Login Logic ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = "User"

if not st.session_state.logged_in:
    email_input = st.text_input("Email")
    pass_input = st.text_input("Password", type="password")
    if st.button("LOG IN"):
        if email_input == "dina@test.com" and pass_input == "123456":
            st.session_state.logged_in = True
            try:
                # Fetching from our new staff_directory table
                user_query = supabase.table("staff_directory").select("full_name").eq("email", email_input).execute()
                st.session_state.username = user_query.data[0]['full_name'] if user_query.data else "Dina"
            except:
                st.session_state.username = "Dina"
            st.rerun()
        else:
            st.error("Access Denied")
else:
    # --- 4. Live Dashboard ---
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    st.subheader("PROPERTY OVERVIEW")
    
    try:
        response = supabase.table("properties").select("*").execute()
        properties = response.data
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", len(properties))
        c2.metric("Done", sum(1 for p in properties if p['status'] == 'Completed'))
        c3.metric("Remaining", sum(1 for p in properties if p['status'] != 'Completed'))
        st.markdown("---")

        # Search & Filter
        search = st.text_input("🔍 Search", "").strip().lower()
        f_status = st.selectbox("🎯 Filter", ["All", "Ready", "In Progress", "Completed"], index=1)
        filtered = [p for p in properties if (search in p['name'].lower()) and (f_status == "All" or p['status'] == f_status)]

        # --- 5. Property Cards ---
        if not filtered:
            st.info("No properties match your filter.")
        else:
            for item in filtered:
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{item['name'].upper()}**")
                        color = "#27AE60" if item['status'] == "Completed" else "#D4AF37"
                        st.markdown(f"<span style='color:{color}'>Status: {item['status']}</span>", unsafe_allow_html=True)
                    with col2:
                        if item['status'] == "In Progress":
                            if st.button("FINISH", key=f"f_{item['id']}"):
                                now = datetime.now().isoformat()
                                supabase.table("properties").update({"status": "Completed", "last_completed_at": now}).eq("id", item['id']).execute()
                                # Stamping history with your Name
                                supabase.table("service_logs").insert({"property_name": item['name'], "status_reached": "Completed", "staff_email": st.session_state.username}).execute()
                                st.rerun()
                        elif item['status'] == "Completed":
                            st.button("DONE", disabled=True, key=f"d_{item['id']}")
                        else:
                            if st.button("START", key=f"s_{item['id']}"):
                                supabase.table("properties").update({"status": "In Progress"}).eq("id", item['id']).execute()
                                st.rerun()

        # --- 6. Manager expansion tools ---
        st.markdown("---")
        with st.expander("➕ ADD NEW PROPERTY"):
            new_name = st.text_input("New Property Name")
            if st.button("Create"):
                if new_name:
                    supabase.table("properties").insert({"name": new_name, "status": "Ready"}).execute()
                    st.success("Added!")
                    st.rerun()

        if st.button("🔄 RESET ALL FOR TOMORROW", use_container_width=True):
            supabase.table("properties").update({"status": "Ready", "last_completed_at": None}).neq("name", "VOID").execute()
            st.rerun()

        # --- 7. Activity Report ---
        st.subheader("📜 RECENT ACTIVITY")
        history = supabase.table("service_logs").select("*").order("finished_at", desc=True).limit(5).execute()
        if history.data:
            st.table(history.data)

    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
