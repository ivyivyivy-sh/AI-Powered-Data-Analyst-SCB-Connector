import streamlit as st
import pandas as pd
import plotly.express as px
from utils import analyze_data_with_ai, generate_insights, clean_data_with_ai, fetch_scb_data

st.set_page_config(page_title="AI Analyst V3 (SCB)", layout="wide")
st.title("🤖 AI Data Analyst V3.0 + 🇸🇪 SCB")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("1. Configuration")
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key Loaded")
    else:
        api_key = st.text_input("Gemini API Key", type="password")

    st.header("2. Data Source")
    # THE NEW SWITCH
    data_source = st.radio("Choose Source:", ["📂 Upload CSV", "☁️ Connect to SCB API"])

    if st.button("Reset / Clear Data"):
        st.session_state.clear()
        st.rerun()

# --- DATA LOADING LOGIC ---
if api_key:
    # A. CSV MODE
    if data_source == "📂 Upload CSV":
        with st.sidebar:
            separator = st.selectbox("CSV Separator", [",", ";", "|", "\t"], index=1)
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            
        if uploaded_file:
            if 'df' not in st.session_state:
                try:
                    st.session_state['df'] = pd.read_csv(uploaded_file, sep=separator)
                    st.toast("CSV Loaded Successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    # B. SCB API MODE (The New Feature)
    else:
        st.subheader("🇸🇪 Connect to Statistics Sweden (SCB)")
        
        # --- THE NEW GUIDE STARTS HERE ---
        with st.expander("❓ How to get the API URL and JSON Query?"):
            st.markdown("""
            **Step 1: Go to the Database**
            * Visit the [SCB Statistics Database (English)](https://www.statistikdatabasen.scb.se/pxweb/en/ssd/).
            
            **Step 2: Select Your Data**
            * Choose a subject (e.g., *Population*) and a table.
            * Select your variables (e.g., *Region: All*, *Year: 2023*).
            * **Important:** Do not select "Select All" for everything, or the dataset will be too large!
            
            **Step 3: Find the API Link**
            * *Before* you click "Show Table", look at the bottom of the page.
            * Click the link that says **"API for this table"** (or similar).
            
            **Step 4: Copy & Paste**
            * **API URL:** Copy the URL shown on that page.
            * **JSON Query:** Copy the full JSON code block.
            * Paste them into the fields below.
            """)
        # --- GUIDE ENDS HERE ---
        
        col1, col2 = st.columns([1, 2])
        with col1:
            scb_url = st.text_input("API URL", placeholder="https://api.scb.se/...")
        with col2:
            scb_query = st.text_area("JSON Query", height=150, placeholder='{"query": [...], "response": {"format": "json"}}')
            
        if st.button("Fetch Data from SCB"):
            if scb_url and scb_query:
                with st.spinner("Connecting to SCB Server..."):
                    try:
                        df_scb = fetch_scb_data(scb_url, scb_query)
                        st.session_state['df'] = df_scb
                        st.success(f"Successfully fetched {len(df_scb)} rows from SCB!")
                    except Exception as e:
                        st.error(str(e))

    # --- MAIN APP LOGIC (Shared for both sources) ---
    if 'df' in st.session_state:
        df = st.session_state['df']
        
        tab1, tab2 = st.tabs(["🧹 Data Sanitizer", "📊 Analysis & Insights"])

        # TAB 1: CLEANING
        with tab1:
            st.subheader("Data Preview & Cleaning")
            st.dataframe(df.head())
            clean_query = st.text_input("Cleaning Instructions", placeholder="e.g. Drop rows where value is 0")
            if st.button("Apply Cleaning"):
                with st.spinner("AI Cleaning..."):
                    try:
                        code = clean_data_with_ai(api_key, df, clean_query)
                        local_vars = {"df": df.copy()}
                        exec(code, {}, local_vars)
                        st.session_state['df'] = local_vars['df']
                        st.success("Cleaned!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        # TAB 2: ANALYSIS
        with tab2:
            st.subheader("Ask Questions")
            query = st.text_area("What do you want to visualize?", placeholder="e.g. Plot Population by Year")
            if st.button("Analyze"):
                with st.spinner("Thinking..."):
                    try:
                        # Analysis
                        code = analyze_data_with_ai(api_key, df, query)
                        local_vars = {"df": df, "px": px}
                        exec(code, {}, local_vars)
                        
                        if "fig" in local_vars:
                            st.plotly_chart(local_vars["fig"], use_container_width=True)
                        elif "result" in local_vars:
                            st.metric("Result", local_vars["result"])
                            
                        # Insights
                        st.markdown("---")
                        st.subheader("💡 Insights")
                        st.info(generate_insights(api_key, df, query))
                        
                        with st.expander("See Code"):
                            st.code(code, language='python')
                    except Exception as e:
                        st.error(f"Error: {e}")

elif not api_key:
    st.warning("Please enter API Key.")