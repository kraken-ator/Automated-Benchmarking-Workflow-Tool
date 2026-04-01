# GenAI-Powered Healthcare Operations Diagnostic Asset 🏥

### **Project Overview**
An automated rapid diagnostic tool designed to benchmark **50,000+ hospital operational records**. This asset identifies systemic inefficiencies in clinical workflows, uncovering **$1.2M in potential cost-efficiency gaps** using a combination of SQL-driven analytics and Generative AI.

### **Tech Stack**
* **Data Engineering:** Python (Pandas, NumPy)
* **Database:** PostgreSQL (Relational modeling & Analytical Views)
* **Intelligence Layer:** Google Gemini API (LLM-driven executive synthesis)
* **Presentation:** Streamlit (Interactive Dashboard)

### **Key Features**
* **Weighted Anomaly Detection:** Engineered a synthetic dataset with weighted distributions to simulate real-world operational "leaks."
* **SQL Transformation Layer:** Developed a PostgreSQL view to calculate "Value at Stake" across ER wait times, Bed Turnover, and Procurement.
* **Automated Insights:** Integrated Gemini 2.5 Flash to synthesize complex metrics into boardroom-ready summaries.

### **How to Run**
1. Clone the repo.
2. Run `generate_diagnostic_data.py` to build the engine.
3. Run `load_postgres.py` to build the DB (Update credentials in script).
4. Run `streamlit run dashboard_app.py` to launch the UI.
