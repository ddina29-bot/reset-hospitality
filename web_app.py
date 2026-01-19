import streamlit as st

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Re set Hospitality Studio", layout="wide")

# --- 2. BRANDING & GREETING ---
# Centered professional business name
st.markdown("<h3 style='text-align: center; color: #555;'>Re set Hospitality Studio</h3>", unsafe_allow_html=True)

# Personal greeting
st.title("👋 Welcome back, Dina")
st.write("Management Dashboard | Overview")
st.divider()

# --- 3. STATUS METRICS (PHASE 1 MOCKUP) ---
# These are just visual placeholders for now
col1, col2, col3 = st.columns(3)
col1.metric("Apartments Ready", "12")
col2.metric("In Progress", "4")
col3.metric("Completed", "8")

st.write("---")

# --- 4. SEARCH & FILTER MOCKUP ---
search = st.text_input("🔍 Search Properties", placeholder="Enter suite number...")
filter_view = st.selectbox("🎯 Filter View", ["All", "Ready", "In Progress", "Completed", "Maintenance"])

# --- 5. PROPERTY LIST (STATIC EXAMPLE) ---
# This shows you how the cards will look once data is flowing
sample_suites = [
    {"name": "101", "status": "Ready", "notes": "Check balcony lock."},
    {"name": "102", "status": "In Progress", "notes": "Waiting for extra towels."},
    {"name": "103", "status": "Maintenance", "notes": "AC unit leaking."}
]

for suite in sample_suites:
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader(f"SUITE {suite['name']}")
            st.write(f"Current Phase: **{suite['status']}**")
            st.text_area("Special Requests", value=suite['notes'], key=f"notes_{suite['name']}")

        with c2:
            st.write("Actions:")
            st.button("🚀 Start", key=f"start_{suite['name']}")
            st.button("✅ Done", key=f"done_{suite['name']}")
            st.button("🔧 Maint.", key=f"maint_{suite['name']}")

# --- 6. SIDEBAR TOOLS ---
with st.sidebar:
    st.header("Management Tools")
    st.button("📊 Generate Report")
    st.divider()
    st.write("Phase 1: Visual Design Only")
