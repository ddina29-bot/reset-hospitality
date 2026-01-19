import streamlit as st
from supabase import create_client, Client

# --- 1. Database Setup ---
SUPABASE_URL = "https://wuqgjkurzstjmhtbdqez.supabase.co"
SUPABASE_KEY = "eyJhbG..." # Use your long key here
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. Luxury Branding ---
st.set_page_config(page_title="RE-SET Hospitality", layout="centered")
GOLD = "#D4AF37"

st.markdown(f"""
    <h1 style='text-align: center; color: black;'>RE-SET</h1>
    <h3 style='text-align: center; color: {GOLD}; font-style: italic;'>Hospitality Studio</h3>
    <hr>
""", unsafe_allow_html=True)

# --- 3. Simple Web Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("LOG IN"):
        try:
            supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.logged_in = True
            st.rerun()
        except:
            st.error("Access Denied")
else:
    # --- 4. Live Dashboard ---
    st.subheader("PROPERTY OVERVIEW")
    
    # Fetch Data
    response = supabase.table("properties").select("id, name, status").execute()
    properties = response.data

    for item in properties:
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**{item['name'].upper()}**")
                status = item.get('status', 'Ready')
                color = "green" if status == "Completed" else "orange"
                st.markdown(f"<span style='color:{color}'>Status: {status}</span>", unsafe_allow_html=True)

            with col2:
                # Button Logic
                if status == "In Progress" or "Progres" in status:
                    if st.button("MARK FINISHED", key=item['id']):
                        supabase.table("properties").update({"status": "Completed"}).eq("id", item['id']).execute()
                        st.rerun()
                elif status == "Completed":
                    st.button("SERVICE DONE", disabled=True, key=item['id'])
                else:
                    if st.button("START SERVICE", key=item['id']):
                        supabase.table("properties").update({"status": "In Progress"}).eq("id", item['id']).execute()
                        st.rerun()

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()