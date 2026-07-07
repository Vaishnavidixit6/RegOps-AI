import streamlit as st
import sqlite3
import os
import sys
import pandas as pd
import requests
import json
from dotenv import load_dotenv

# Load project environment variables (including GEMINI_API_KEY)
load_dotenv()

# Add the current directory to path to resolve app imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

st.set_page_config(
    page_title="Regulatory Intelligence Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# DB Helper
# ----------------------------------------------------
def get_db_data(query):
    conn = sqlite3.connect("bank_knowledge.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ----------------------------------------------------
# Streamlit Custom Style / Header
# ----------------------------------------------------
st.markdown("""
<style>
    .report-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .report-subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .task-badge {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="report-title">⚖️ Agentic Regulatory Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="report-subtitle">Leveraging a Multi-Agent ADK network to automatically analyze RBI Circulars, audit internal policies, flag non-compliant branch files, and generate security recommendations.</div>', unsafe_allow_html=True)

# Ensure database is seeded
if not os.path.exists("bank_knowledge.db"):
    st.error("Database bank_knowledge.db not found. Please run the seeding script first.")
    if st.button("Seed Database Now"):
        import init_db
        init_db.init_database()
        st.success("Database seeded successfully!")
        st.rerun()

# ----------------------------------------------------
# Sidebar - Database & SOP Explorer
# ----------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/law.png", width=80)
    st.header("Bank Knowledge Explorer")
    st.write("Browse internal records stored in the SQLite database:")
    
    inspect_type = st.selectbox(
        "Select Record Type",
        ["Pending Loan Applications", "Internal Bank SOPs", "Fraud Advisories", "RBI Circulars Catalog"]
    )
    
    if inspect_type == "Pending Loan Applications":
        df = get_db_data("SELECT application_id, customer_name, product_type, requested_amount, status, kyc_status, verification_details FROM loan_applications")
        st.dataframe(df, use_container_width=True)
        st.caption("Notice LAP-213: Stalled due to a missing Video-KYC (V-CIP) session and an amount exceeding standard thresholds.")
    
    elif inspect_type == "Internal Bank SOPs":
        df = get_db_data("SELECT sop_code, title, product_type, last_updated, content FROM internal_sops")
        for idx, row in df.iterrows():
            with st.expander(f"{row['sop_code']} - {row['title']}"):
                st.write(f"**Product Type:** {row['product_type']}")
                st.write(f"**Last Updated:** {row['last_updated']}")
                st.write(row['content'])
                
    elif inspect_type == "Fraud Advisories":
        df = get_db_data("SELECT advisory_code, title, issue_date, threat_level, content FROM fraud_advisories")
        for idx, row in df.iterrows():
            with st.expander(f"{row['advisory_code']} - {row['title']} [{row['threat_level']}]"):
                st.write(f"**Issue Date:** {row['issue_date']}")
                st.write(row['content'])
                
    elif inspect_type == "RBI Circulars Catalog":
        df = get_db_data("SELECT circular_number, title, issue_date, effective_date, status, content FROM rbi_circulars")
        for idx, row in df.iterrows():
            with st.expander(f"{row['circular_number']} - {row['title']}"):
                st.write(f"**Issue Date:** {row['issue_date']} | **Status:** {row['status']}")
                st.write(row['content'])

# ----------------------------------------------------
# Main Panel Tabs
# ----------------------------------------------------
tab1, tab2 = st.tabs(["📢 RBI Circular Impact Analyzer", "📋 Loan Application Checker"])

server_url = "http://127.0.0.1:8000"

# ----------------------------------------------------
# TAB 1: RBI Circular Impact Analyzer
# ----------------------------------------------------
with tab1:
    st.subheader("📝 Input New RBI Circular Text")
    
    CIP_TEXT_NEW = """Effective July 1, 2026, the RBI amends the KYC directions to mandate that all non-face-to-face onboarding for individuals and sole proprietorships must be completed utilizing the Video-based Customer Identification Process (V-CIP). Physical document verification is replaced by digital e-KYC or e-PAN database checks. V-CIP sessions must be recorded live, require real-time geographical geotagging to ensure the customer is inside India, and integrate AI facial matching with liveness checks. Any digital account opened without a compliant V-CIP session must be frozen within 7 days of opening."""

    custom_circular = st.text_area(
        "Paste the regulatory text below:",
        value=CIP_TEXT_NEW,
        height=150
    )

    run_btn = st.button("🚀 Run Comprehensive Regulatory Audit Pipeline", type="primary")

    if run_btn:
        st.info("Checking connection to the local ADK Agent server...")
        try:
            session_resp = requests.post(f"{server_url}/apps/app/users/streamlit-user/sessions", json={}, timeout=5)
            if session_resp.status_code != 200:
                st.error(f"Failed to connect to agent server: HTTP {session_resp.status_code}. Is the server running?")
                st.stop()
            session_id = session_resp.json().get("id")
        except Exception as e:
            st.error(f"Could not connect to the agent server at {server_url}. Please ensure the server is started in the workspace by running: `uv run python app/fast_api_app.py`.\n\nError: {e}")
            st.stop()
            
        st.success(f"Connected successfully! (Session ID: {session_id})")
        
        st.write("---")
        
        # Placeholders for streaming sub-agents log
        st.subheader("🕵️ Sub-Agent Live Impact Analysis")
        circular_analysis_container = st.empty()
        
        st.subheader("🔄 Policy Gaps & Version Differences")
        policy_diff_container = st.empty()
        
        st.subheader("📂 Branch File Review")
        cases_container = st.empty()
        
        st.subheader("🔍 Supporting Fraud & Threat Evidence")
        evidence_container = st.empty()
        
        st.subheader("📄 Unified Compliance Audit Report")
        recommendation_container = st.empty()
        
        prompt = f"Perform a comprehensive compliance analysis. The new regulation states: '{custom_circular}'. Please run the circular analysis, policy gap check against our SOPs, case audits on pending applications, evidence gather for fraud or historical guidelines, and construct a final list of recommendations. You must show output from each sub-agent."
        
        payload = {
            "app_name": "app",
            "user_id": "streamlit-user",
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": prompt}],
            },
        }
        
        collected_responses = {}
        
        try:
            response = requests.post(f"{server_url}/run_sse", json=payload, stream=True, timeout=120)
            if response.status_code != 200:
                st.error(f"Failed to run agent (HTTP {response.status_code}): {response.text}")
                st.stop()
                
            for line in response.iter_lines(decode_unicode=True):
                if not isinstance(line, str) or not line.startswith("data: "):
                    continue
                data_str = line[len("data: ") :]
                try:
                    event = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                    
                author = event.get("author")
                content = event.get("content")
                
                if content and isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if "text" in part and part["text"].strip():
                            txt = part["text"]
                            
                            if author == "circular_analysis_agent":
                                if "circular_analysis_agent" not in collected_responses:
                                    collected_responses["circular_analysis_agent"] = ""
                                collected_responses["circular_analysis_agent"] += txt
                                circular_analysis_container.info(f"**Circular Analysis Agent**\n\n{collected_responses['circular_analysis_agent']}")
                                
                            elif author == "policy_diff_agent":
                                if "policy_diff_agent" not in collected_responses:
                                    collected_responses["policy_diff_agent"] = ""
                                collected_responses["policy_diff_agent"] += txt
                                policy_diff_container.success(f"**Policy Diff Agent**\n\n{collected_responses['policy_diff_agent']}")
                                
                            elif author == "impacted_cases_agent":
                                if "impacted_cases_agent" not in collected_responses:
                                    collected_responses["impacted_cases_agent"] = ""
                                collected_responses["impacted_cases_agent"] += txt
                                cases_container.warning(f"**Impacted Cases Agent**\n\n{collected_responses['impacted_cases_agent']}")
                                
                            elif author == "evidence_supporting_agent":
                                if "evidence_supporting_agent" not in collected_responses:
                                    collected_responses["evidence_supporting_agent"] = ""
                                collected_responses["evidence_supporting_agent"] += txt
                                evidence_container.error(f"**Evidence Supporting Agent**\n\n{collected_responses['evidence_supporting_agent']}")
                                
                            elif author == "recommendation_agent" or author == "regulatory_intelligence_coordinator":
                                if "recommendation_agent" not in collected_responses:
                                    collected_responses["recommendation_agent"] = ""
                                collected_responses["recommendation_agent"] += txt
                                recommendation_container.markdown(f"{collected_responses['recommendation_agent']}")
                                
            st.balloons()
            st.success("Regulatory compliance audit successfully finished!")
            
            # Compliance Report Downloader (Task 5)
            final_report = (
                f"# COMPLIANCE REPORT & AUDIT RECOMMENDATIONS\n\n"
                f"### CIRCULAR ANALYSIS:\n{collected_responses.get('circular_analysis_agent', 'N/A')}\n\n"
                f"### POLICY GAPS & VERSION COMPARE:\n{collected_responses.get('policy_diff_agent', 'N/A')}\n\n"
                f"### CASE AUDIT LOGS:\n{collected_responses.get('impacted_cases_agent', 'N/A')}\n\n"
                f"### EVINDENCE & THREAT SHIELD:\n{collected_responses.get('evidence_supporting_agent', 'N/A')}\n\n"
                f"### ACTIONABLE ADVICE:\n{collected_responses.get('recommendation_agent', 'N/A')}"
            )
            st.download_button(
                label="📥 Download Signed Compliance Report (.md)",
                data=final_report,
                file_name="compliance_audit_report.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.exception(e)

# ----------------------------------------------------
# TAB 2: Loan Application Checker (Officer Flow)
# ----------------------------------------------------
with tab2:
    st.subheader("📋 Audit Loan Application File")
    st.write("Select a pending customer loan application from the database to inspect details and query governing circulars:")
    
    # Load application IDs dynamically
    app_ids = get_db_data("SELECT application_id FROM loan_applications")["application_id"].tolist()
    
    selected_app_id = st.selectbox("Select Application ID to Audit", app_ids)
    
    # Fetch details
    conn = sqlite3.connect("bank_knowledge.db")
    cursor = conn.cursor()
    cursor.execute("SELECT customer_name, product_type, requested_amount, status, kyc_status, verification_details FROM loan_applications WHERE application_id = ?", (selected_app_id,))
    app_record = cursor.fetchone()
    conn.close()
    
    if app_record:
        cust_name, prod_type, amount, app_status, kyc_status, verification_details = app_record
        
        # Display current info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Customer Name", cust_name)
            st.metric("Loan Status", app_status)
        with col2:
            st.metric("Product Type", prod_type)
            st.metric("KYC Status", kyc_status)
        with col3:
            st.metric("Requested Amount", f"INR {amount:,.2f}")
            
        st.text_area("Verification Log & Details", value=verification_details, height=100, disabled=True)
        
        run_app_audit_btn = st.button(f"🔍 Run Compliance Review for {selected_app_id}", type="primary")
        
        if run_app_audit_btn:
            st.info("Checking connection to the local ADK Agent server...")
            try:
                session_resp = requests.post(f"{server_url}/apps/app/users/streamlit-user/sessions", json={}, timeout=5)
                if session_resp.status_code != 200:
                    st.error(f"Failed to connect to agent server. Is the server running?")
                    st.stop()
                session_id = session_resp.json().get("id")
            except Exception as e:
                st.error(f"Could not connect to the agent server at {server_url}.\n\nError: {e}")
                st.stop()
                
            st.success(f"Connected successfully! (Session ID: {session_id})")
            
            st.write("---")
            
            # Decoupled Sub-Agent Output Containers for Tab 2
            st.subheader("🕵️ RBI Circular Impact Analysis")
            app_circular_container = st.empty()
            
            st.subheader("🔄 Version and Gap Compare")
            app_policy_container = st.empty()
            
            st.subheader("📋 Loan File Review and Audit")
            app_loan_container = st.empty()
            
            st.subheader("🛡️ Active Fraud Shield")
            app_fraud_container = st.empty()
            
            st.subheader("📄 Compliance Report Generator")
            app_rec_container = st.empty()
            
            # Direct prompt asking the agent to search matching circulars and provide compliance advice
            app_prompt = (
                f"Please audit this specific loan application: ID={selected_app_id}, Customer={cust_name}, Product={prod_type}, "
                f"Amount={amount}, KYC Status={kyc_status}, Verification={verification_details}.\n"
                f"You must:\n"
                f"1. Search active and relevant RBI circulars using the search_rbi_circulars tool matching this product or verification method.\n"
                f"2. Inspect internal SOPs using the search_sops tool governing this loan type.\n"
                f"3. Explain which specific RBI circulars (circular number and titles) the loan officer must refer to for this file.\n"
                f"4. State clearly if this application complies with those circulars and identify any compliance gaps or required actions.\n"
                f"5. Search active fraud advisories (using the search_fraud_advisories tool) matching the verification method of this file (e.g. check for online/digital onboarding threats, deepfakes, or GPS spoofing if the application was done online) and explicitly flag any potential fraud risks or security alerts that apply to this file."
            )
            
            payload = {
                "app_name": "app",
                "user_id": "streamlit-user",
                "session_id": session_id,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": app_prompt}],
                },
            }
            
            collected_responses = {}
            
            try:
                response = requests.post(f"{server_url}/run_sse", json=payload, stream=True, timeout=120)
                if response.status_code != 200:
                    st.error(f"Failed to run agent: {response.text}")
                    st.stop()
                    
                for line in response.iter_lines(decode_unicode=True):
                    if not isinstance(line, str) or not line.startswith("data: "):
                        continue
                    data_str = line[len("data: ") :]
                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                        
                    author = event.get("author")
                    content = event.get("content")
                    if content and isinstance(content, dict):
                        parts = content.get("parts", [])
                        for part in parts:
                            if "text" in part and part["text"].strip():
                                txt = part["text"]
                                
                                if author == "circular_analysis_agent":
                                    if "app_circular" not in collected_responses:
                                        collected_responses["app_circular"] = ""
                                    collected_responses["app_circular"] += txt
                                    app_circular_container.info(f"**Circular Analysis Agent**\n\n{collected_responses['app_circular']}")
                                    
                                elif author == "policy_diff_agent":
                                    if "app_policy" not in collected_responses:
                                        collected_responses["app_policy"] = ""
                                    collected_responses["app_policy"] += txt
                                    app_policy_container.success(f"**Policy Diff Agent**\n\n{collected_responses['app_policy']}")
                                    
                                elif author == "impacted_cases_agent":
                                    if "app_loan" not in collected_responses:
                                        collected_responses["app_loan"] = ""
                                    collected_responses["app_loan"] += txt
                                    app_loan_container.warning(f"**Impacted Cases Agent**\n\n{collected_responses['app_loan']}")
                                    
                                elif author == "evidence_supporting_agent":
                                    if "app_fraud" not in collected_responses:
                                        collected_responses["app_fraud"] = ""
                                    collected_responses["app_fraud"] += txt
                                    app_fraud_container.error(f"**Evidence Supporting Agent**\n\n{collected_responses['app_fraud']}")
                                    
                                elif author == "recommendation_agent" or author == "regulatory_intelligence_coordinator":
                                    if "app_rec" not in collected_responses:
                                        collected_responses["app_rec"] = ""
                                    collected_responses["app_rec"] += txt
                                    app_rec_container.markdown(f"{collected_responses['app_rec']}")
                                    
                st.balloons()
                st.success("Application compliance reference audit finished successfully!")
                
                # Compliance Report Downloader (Task 5)
                final_app_report = (
                    f"# APPLICATION COMPLIANCE REPORT ({selected_app_id})\n\n"
                    f"### APPLICABLE RBI CIRCULARS:\n{collected_responses.get('app_circular', 'N/A')}\n\n"
                    f"### INTERNAL POLICY GAP AUDIT:\n{collected_responses.get('app_policy', 'N/A')}\n\n"
                    f"### CASE FILE COMPLIANCE CHECK:\n{collected_responses.get('app_loan', 'N/A')}\n\n"
                    f"### ACTIVE FRAUD WARNINGS:\n{collected_responses.get('app_fraud', 'N/A')}\n\n"
                    f"### AUDITOR CHECKLIST & DISCLAIMERS:\n{collected_responses.get('app_rec', 'N/A')}"
                )
                st.download_button(
                    label=f"📥 Download Application Compliance Report ({selected_app_id})",
                    data=final_app_report,
                    file_name=f"compliance_report_{selected_app_id}.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.exception(e)
