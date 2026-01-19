import streamlit as st
from supabase import create_client, Client

# --- 1. Database Setup ---
SUPABASE_URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cWdqa3VyenN0am1odGJkcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjU5MTcsImV4cCI6MjA4NDQwMTkxN30.uealUGFmT7qiX_eA3Ya-cuW9KJYcBg-et18iaEdppEs" # Make sure this is your SERVICE_ROLE key or ANON key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. Luxury Branding ---
st.set_page_config(page_title="RE-SET Hospitality", layout="centered")
GOLD = "#D4AF37"

st.markdown(f"<h1 style='text-align: center;'>RE-SET</h1><h3 style='text-align: center; color: {GOLD};'>Hospitality Studio</h3><hr>", unsafe_allow_html=True)

# --- 3. Bypass Login (For Testing Only) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    # We use a simple 'if' check here to bypass the Supabase Auth gate for a moment
    if st.button("LOG IN"):
        if email == "dina@test.com" and password == "123456": # Use a simple temporary password
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Temporary Bypass Failed. Check your typing.")
else:
    # --- 4. Live Dashboard ---
    st.subheader("PROPERTY OVERVIEW")
    
    try:
        # Fetching your clean property list
        response = supabase.table("properties").select("id, name, status").execute()
        properties = response.data

        for item in properties:
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
    except Exception as e:
        st.error(f"Database Error: {e}")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

