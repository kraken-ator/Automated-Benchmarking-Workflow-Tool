import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
from google import genai
from google.genai import types

# 1. Database Connection 
db_user = 'postgres'
db_password = urllib.parse.quote_plus('PASSWORD') 
db_host = 'localhost'
db_port = '5432'
db_name = 'postgres' 

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# 2. Initialize the NEW Gemini Client
# ---> YOU MUST PUT YOUR REAL API KEY HERE <---
client = genai.Client(api_key='API KEY')

# 3. The "Consultant" SQL Query
diagnostic_query = """
SELECT 
    facility, 
    department, 
    SUM(er_leakage_usd) AS total_er_leakage,
    SUM(bed_leakage_usd) AS total_bed_leakage,
    SUM(proc_leakage_usd) AS total_proc_leakage,
    SUM(total_variance_usd) AS total_leakage
FROM client_ops.vw_diagnostic_anomalies
WHERE total_variance_usd > 0
GROUP BY facility, department
ORDER BY total_leakage DESC
LIMIT 5;
"""

print("Extracting top operational leaks from PostgreSQL...")
with engine.connect() as conn:
    df_top_leaks = pd.read_sql(diagnostic_query, conn)

data_context = df_top_leaks.to_string(index=False)

# 4. The Prompt Engineering
system_instruction = """
You are a Senior Engagement Manager at a top-tier management consulting firm specializing in Healthcare Operations.
Your goal is to analyze the provided data of hospital operational leaks and write a brief, high-impact executive summary.
Focus on the 'Value at Stake' (the financial leakage).
Use professional consulting terminology. Keep it under 150 words.
Structure it with a brief intro, 2-3 bullet points on the key drivers, and a concluding recommendation.
Do not use any specific consulting firm names in your response.
"""

user_prompt = f"Here is the aggregated diagnostic data showing the top 5 areas of financial leakage:\n\n{data_context}\n\nPlease provide the executive summary."

# 5. Execute the Gemini API Call using the new SDK
print("Analyzing anomalies with Google Gemini...\n")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=f"{system_instruction}\n\n{user_prompt}",
    config=types.GenerateContentConfig(
        temperature=0.3,
    )
)

# 6. Output the Result
print("=== EXECUTIVE DIAGNOSTIC SUMMARY ===")
print(response.text)
print("====================================")