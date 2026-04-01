import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import plotly.express as px
from google import genai
from google.genai import types

# --- 1. Configuration & Credentials ---
st.set_page_config(page_title="Clinical Ops Diagnostic", layout="wide")

# ---> DROP YOUR GEMINI API KEY HERE <---
GEMINI_API_KEY = "API KEY"

@st.cache_resource
def init_db_connection():
    db_user = 'postgres'
    db_password = urllib.parse.quote_plus('sc@m4ps') 
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'postgres'
    return create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

engine = init_db_connection()

# --- 2. Data Extraction ---
@st.cache_data
def load_diagnostic_data():
    query = """
    SELECT 
        facility, 
        department, 
        SUM(er_leakage_usd) AS er_leakage,
        SUM(bed_leakage_usd) AS bed_leakage,
        SUM(proc_leakage_usd) AS proc_leakage,
        SUM(total_variance_usd) AS total_leakage
    FROM client_ops.vw_diagnostic_anomalies
    WHERE total_variance_usd > 0
    GROUP BY facility, department
    ORDER BY total_leakage DESC
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

df = load_diagnostic_data()

# --- 3. Dashboard Header & KPIs ---
st.title("🏥 Rapid Diagnostic Asset: Operational Value at Stake")
st.markdown("---")

# Calculate totals for the top KPI row
total_value_at_stake = df['total_leakage'].sum()
total_er = df['er_leakage'].sum()
total_bed = df['bed_leakage'].sum()
total_proc = df['proc_leakage'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Value at Stake", f"${total_value_at_stake:,.0f}")
col2.metric("ER Wait Time Variance", f"${total_er:,.0f}")
col3.metric("Bed Turnover Variance", f"${total_bed:,.0f}")
col4.metric("Procurement Variance", f"${total_proc:,.0f}")

st.markdown("---")

# --- 4. Interactive Visualizations ---
st.subheader("Leakage Breakdown by Facility & Department")

# Plotly Bar Chart
fig = px.bar(
    df, 
    x="facility", 
    y=["er_leakage", "bed_leakage", "proc_leakage"],
    color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"],
    title="Financial Variance Drivers",
    labels={"value": "Leakage (USD)", "variable": "Driver", "facility": "Hospital Facility"},
    barmode="stack"
)
st.plotly_chart(fig, use_container_width=True)

# --- 5. GenAI Executive Summary Integration ---
st.markdown("---")
st.subheader("🧠 GenAI Diagnostic Summary")

if st.button("Generate Executive Insights"):
    with st.spinner("Analyzing operational data with Gemini..."):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Get top 5 offenders for the prompt
            top_5_data = df.head(5).to_string(index=False)
            
            system_instruction = """
            You are a Senior Engagement Manager at a top-tier management consulting firm specializing in Healthcare Operations.
            Your goal is to analyze the provided data of hospital operational leaks and write a brief, high-impact executive summary.
            Focus on the 'Value at Stake' (the financial leakage).
            Use professional consulting terminology. Keep it under 150 words.
            Structure it with a brief intro, 2-3 bullet points on the key drivers, and a concluding recommendation.
            """
            
            user_prompt = f"Here is the aggregated diagnostic data showing the top 5 areas of financial leakage:\n\n{top_5_data}\n\nPlease provide the executive summary."
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{system_instruction}\n\n{user_prompt}",
                config=types.GenerateContentConfig(temperature=0.3)
            )
            
            st.success("Analysis Complete")
            st.info(response.text)
            
        except Exception as e:
            st.error(f"Error connecting to AI API: {e}")