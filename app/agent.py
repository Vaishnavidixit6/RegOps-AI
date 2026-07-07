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
        model="gemini-2.0-flash-lite",
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
        model="gemini-2.0-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You identify differences between the new regulatory circular policies/clauses and existing internal bank policies/SOPs. "
        "Use bank knowledge search tools to retrieve the existing SOPs and compare them to find the gaps."
    ),
    description="Compares new regulatory circulars against existing internal bank policies to identify policy differences.",
    tools=[bank_knowledge_tools],
)

# 3. Impacted Cases Agent
impacted_cases_agent = Agent(
    name="impacted_cases_agent",
    model=Gemini(
        model="gemini-2.0-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You must evaluate which exact pending branch cases or loan applications are affected by the new regulatory guidelines. "
        "Follow these steps:\n"
        "1. Call the list_pending_loan_applications tool to get all pending applications (which contains their customer name, product, amount, KYC status, and verification details).\n"
        "2. Parse the returned list directly. Compare the verification details of each pending application against the new V-CIP circular (e.g. check if the application is digital/remote and if a V-CIP session was completed; if not, flag it as non-compliant).\n"
        "3. Focus on calling out the exact non-compliant applications (e.g., 'LAP-213'), the customer name, the loan product, the amount, and the precise compliance violation.\n"
        "4. You only need to call get_loan_application if you need to fetch extra historical details not shown in the list."
    ),
    description="Identifies specific customer files, branch cases, or loan applications that will be impacted by the new regulation.",
    tools=[bank_knowledge_tools],
)

# 4. Evidence Supporting Agent
evidence_supporting_agent = Agent(
    name="evidence_supporting_agent",
    model=Gemini(
        model="gemini-2.0-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You search internal bank SOPs, fraud advisories, and historical RBI circulars to find supporting evidence, guidelines, "
        "or potential security/fraud threats related to the new regulation."
    ),
    description="Searches for supporting evidence, historical circulars, SOPs, and fraud advisories.",
    tools=[bank_knowledge_tools],
)

# 5. Recommendation Agent
recommendation_agent = Agent(
    name="recommendation_agent",
    model=Gemini(
        model="gemini-2.0-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You synthesize the circular analysis, policy differences, impacted cases, and supporting evidence to formulate actionable compliance recommendations. "
        "ALWAYS include a disclaimer: 'Recommendations are advisory only and final decisions rest with authorized bank personnel.'"
    ),
    description="Provides structured compliance recommendations and action steps.",
)

# Root Coordinator Agent
root_agent = Agent(
    name="regulatory_intelligence_coordinator",
    model=Gemini(
        model="gemini-2.0-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Regulatory Intelligence Platform Coordinator. When a user asks you to analyze a regulatory change or new RBI circular, "
        "delegate tasks to your sub-agents: circular_analysis_agent, policy_diff_agent, impacted_cases_agent, evidence_supporting_agent, "
        "and recommendation_agent. Combine their responses into a single, comprehensive, and cohesive report. "
        "Always present the final output with clear sections: Circular Analysis, Policy Diff, Impacted Cases, Supporting Evidence, and Recommendations. "
        "At the end of your response, output a prominent warning/disclaimer: 'DISCLAIMER: All recommendations are advisory only. Final decisions rest with authorized bank personnel.'"
    ),
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
