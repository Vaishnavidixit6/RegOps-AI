# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Initialize the MCP Toolset to connect to our local Bank Knowledge MCP Server
bank_knowledge_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "bank_knowledge_mcp.py"],
        )
    )
)

# 1. Circular Analysis Agent
circular_analysis_agent = Agent(
    name="circular_analysis_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You analyze new regulatory circulars. Extract effective dates, products affected, "
        "changed clauses, and removed clauses. Summarize your findings clearly and concisely."
    ),
    description="Extracts details from RBI circulars including effective date, affected products, changed clauses, and removed clauses.",
)

# 2. Policy Diff Agent
policy_diff_agent = Agent(
    name="policy_diff_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You identify differences between the new regulatory circular and existing internal bank policies/SOPs. "
        "Follow these steps:\n"
        "1. Use bank knowledge search tools to query the exact internal SOPs matching the circular's product type (e.g. query 'KYC' or 'Personal Loan').\n"
        "2. In your gap analysis, state the exact incoming circular number (e.g. RBI/2026-27/045) and compare it directly to the exact internal SOP codes (e.g. SOP-KYC-001) retrieved from the database.\n"
        "3. Highlight specific clauses and versions that must be updated. Never generalize or hallucinate; only cite exact records from the database."
    ),
    description="Compares new regulatory circulars against existing internal bank policies to identify policy differences.",
    tools=[bank_knowledge_tools],
)

# 3. Impacted Cases Agent
impacted_cases_agent = Agent(
    name="impacted_cases_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You must evaluate which exact pending branch cases or loan applications are affected by the new regulatory guidelines. "
        "Follow these steps:\n"
        "1. Call the list_pending_loan_applications tool to get all pending applications from the database.\n"
        "2. Parse the database results directly. Count the exact number of pending loan applications returned (this should be the actual count from the database, which is a small number around 10-15 cases total).\n"
        "3. Review the verification details of each pending application to check compliance (e.g. flag those digital signups that lack Video-KYC/V-CIP sessions).\n"
        "4. Output a clear summary naming the exact application IDs (e.g., 'LAP-213'), the customer name, the loan product, the amount, and the precise compliance violation.\n"
        "5. NEVER fabricate or generalize numbers (do NOT say '1,240 applications' or invent other metrics). Only state the exact counts and IDs returned by the database tool."
    ),
    description="Identifies specific customer files, branch cases, or loan applications that will be impacted by the new regulation.",
    tools=[bank_knowledge_tools],
)

# 4. Evidence Supporting Agent
evidence_supporting_agent = Agent(
    name="evidence_supporting_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You search internal bank databases for supporting evidence, historical circular guidelines, and fraud advisories. "
        "Follow these steps:\n"
        "1. Search active fraud advisories (using search_fraud_advisories) and historical circulars (using search_rbi_circulars) matching the context (e.g. 'V-CIP', 'KYC', or 'GPS').\n"
        "2. State the exact historical circular numbers (e.g., RBI/2026-27/010) and exact fraud advisory codes (e.g. ADV-2026-012) retrieved from the database.\n"
        "3. Explicitly describe the security threats (e.g. deepfakes, GPS spoofing) found in the database records. Never invent or generalize titles; only use facts from the database."
    ),
    description="Searches for supporting evidence, historical circulars, SOPs, and fraud advisories.",
    tools=[bank_knowledge_tools],
)

# 5. Recommendation Agent
recommendation_agent = Agent(
    name="recommendation_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You synthesize the circular analysis, policy differences, impacted cases, and supporting evidence to formulate actionable compliance recommendations. "
        "Make sure to reference the specific circular numbers, SOP codes, and loan application IDs in your checklist.\n"
        "ALWAYS include a disclaimer: 'Recommendations are advisory only and final decisions rest with authorized bank personnel.'"
    ),
    description="Provides structured compliance recommendations and action steps.",
)

# Root Coordinator Agent
root_agent = Agent(
    name="regulatory_intelligence_coordinator",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Regulatory Intelligence Platform Coordinator. When a user asks you to analyze a regulatory change or new RBI circular, "
        "delegate tasks to your sub-agents: circular_analysis_agent, policy_diff_agent, impacted_cases_agent, evidence_supporting_agent, "
        "and recommendation_agent. Combine their responses into a single, comprehensive, and cohesive report. "
        "Always present the final output with clear sections: Circular Analysis, Policy Diff, Impacted Cases, Supporting Evidence, and Recommendations. "
        "At the end of your response, output a prominent warning/disclaimer: 'DISCLAIMER: All recommendations are advisory only. Final decisions rest with authorized bank personnel.'"
    ),
    description="Main coordinator agent that orchestrates circular analysis and compliance auditing.",
    sub_agents=[
        circular_analysis_agent,
        policy_diff_agent,
        impacted_cases_agent,
        evidence_supporting_agent,
        recommendation_agent,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
