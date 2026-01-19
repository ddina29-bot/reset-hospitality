import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# --- 1. Database Setup ---
# PASTE YOUR ACTUAL SUPABASE KEY INSIDE THE QUOTES BELOW
SUPABASE_URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs" 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. Branding ---
st.set_page_config(page_title="RE-SET Hospitality", layout="centered")
GOLD = "#D4AF37"
st.markdown(f"<h1 style='text-align: center;'>RE-SET</h1><h3 style='text-align: center; color: {GOLD};'>Hospitality Studio</h3>", unsafe_allow_html=True)

# --- 3. Login Logic ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = "User"

if not st.session_state.logged_in:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("LOG IN"):
        if email == "dina@test.com" and password == "123456":
            st.session_state.logged_in = True
            try:
                # Fetches your name "Dina" from the staff_directory table
                user_query = supabase.table("staff_directory").select("full_name").eq("email", email).execute()
                st.session_state.username = user_query.data[0]['full_name'] if user_query.data else "Dina"
            except: 
                st.session_state.username = "Dina"
            st.rerun()
        else:
            st.error("Access Denied")
else:
    # Centered Greeting
    st.markdown(f"<p style='text-align: center;'>Welcome back, <b>{st.session_state.username}</b>! 👋</p>", unsafe_allow_html=True)
    
    # --- 4. Navigation Tabs ---
    tab1, tab2 = st.tabs(["🚀 LIVE DASHBOARD", "📜 PERFORMANCE REPORTS"])

    with tab1:
        try:
            response = supabase.table("properties").select("*").execute()
            properties = response.data
            
            # Overview Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Total", len(properties))
            c2.metric("Done", sum(1 for p in properties if p['status'] == 'Completed'))
            c3.metric("Remaining", sum(1 for p in properties if p['status'] != 'Completed'))
            
            # Filtering Tools
            search = st.text_input("🔍 Search", "").strip().lower()
            f_status = st.selectbox("🎯 Filter", ["All", "Ready", "In Progress", "Completed"], index=0)
            filtered = [p for p in properties if (search in p['name'].lower()) and (f_status == "All" or p['status'] == f_status)]

            # --- 5. Property Cards ---
            for item in filtered:
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{item['name'].upper()}**")
                        status = item.get('status', 'Ready')
                        color = "#27AE60" if status == "Completed" else "#D4AF37"
                        st.markdown(f"<span style='color:{color}'>Status: {status}</span>", unsafe_allow_html=True)
                        
                        # TIME FIX: Displays the finish time on the card
                        if status == "Completed" and item.get('last_completed_at'):
                            formatted_time = item['last_completed_at'][:16].replace('T', ' ')
                            st.caption(f"✅ Finished at: {formatted_time}")
                        
                        # NOTES FIX: Fetches and saves Special Instructions
                        current_note = item.get('notes') if item.get('notes') else ""
                        new_note = st.text_input("Special Instructions", value=current_note, key=f"n_{item['id']}")
                        if new_note != current_note:
                            supabase.table("properties").update({"notes": new_note}).eq("id", item['id']).execute()
                            st.toast(f"Instructions updated for {item['name']}")

                    with col2:
                        # Start/Finish Buttons
                        if status == "In Progress":
                            if st.button("FINISH", key=f"f_{item['id']}"):
                                now = datetime.now().isoformat()
                                # 1. Update Property Status
                                supabase.table("properties").update({"status": "Completed", "last_completed_at": now}).eq("id", item['id']).execute()
                                # 2. Record Who & When to History
                                supabase.table("service_logs").insert({
                                    "property_name": item['name'], 
                                    "status_reached": "Completed", 
                                    "staff_email": st.session_state.username
                                }).execute()
                                st.rerun()
                        elif status == "Completed":
                            st.button("DONE", disabled=True, key=f"d_{item['id']}")
                        else:
                            if st.button("START", key=f"s_{item['id']}"):
                                supabase.table("properties").update({"status": "In Progress"}).eq("id", item['id']).execute()
                                st.rerun()
            
            # --- 6. Manager Tools ---
            st.markdown("---")
            st.subheader("MANAGER TOOLS")
            if st.button("🔄 RESET ALL FOR TOMORROW", use_container_width=True):
                supabase.table("properties").update({"status": "Ready", "last_completed_at": None}).neq("name", "VOID").execute()
                st.rerun()
            
            with st.expander("➕ ADD NEW PROPERTY"):
                new_p = st.text_input("Property Name (e.g., Suite 102)")
                if st.button("Add to Studio"):
                    if new_p:
                        supabase.table("properties").insert({"name": new_p, "status": "Ready"}).execute()
                        st.rerun()

        except Exception as e: 
            st.error(f"Error: {e}")

    with tab2:
        # --- 7. History Report ---
        st.subheader("Historical Activity Log")
        try:
            history = supabase.table("service_logs").select("*").order("finished_at", desc=True).execute()
            if history.data: 
                st.dataframe(history.data, use_container_width=True)
            else: 
                st.info("No activity recorded yet.")
        except Exception as e: 
            st.error(f"Could not load history: {e}")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
