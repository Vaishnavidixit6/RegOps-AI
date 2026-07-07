# RegShield AI
## An Agentic Regulatory Intelligence Platform for Banking Compliance

---

### 1. The Problem
Every day, bank officers make hundreds of decisions that directly affect customers and the institution's financial and regulatory risk. While experienced officers often rely on years of practical knowledge, newly recruited officers and employees handling unfamiliar cases face a much harder challenge: keeping up with constantly changing regulations.

Banks regularly receive new RBI circulars, internal policy updates, fraud advisories, and revised Standard Operating Procedures (SOPs). Officers are expected to understand these changes immediately while continuing to process customer requests such as loan sanctions, KYC verification, account opening, and digital banking services. In practice, it is unrealistic for every employee to remember every policy change, especially when multiple circulars are issued within a short period.

As a result:
*   Loan applications may be sanctioned using outdated policies.
*   Mandatory verification steps, such as updated KYC or Video-KYC (V-CIP) requirements, may be overlooked.
*   Officers spend valuable time searching through lengthy circulars or consulting senior colleagues before making a decision.
*   Managers and auditors must later identify mistakes manually, resulting in delays, audit compliance findings, customer dissatisfaction, and avoidable financial risks.

The challenge is not a lack of competence among bank officers; rather, the volume and frequency of regulatory updates have outgrown what humans can realistically track and apply consistently.

---

### 2. Why Agents?
A single LLM acting as a chatbot cannot efficiently coordinate document comparison, policy retrieval, database analysis, evidence gathering, and recommendation generation. Doing so results in context bloat, hallucinated database queries, and a lack of modular audit trails. 

RegShield AI (RegOps AI) uses specialized AI agents that collaborate to complete an end-to-end compliance workflow. By separating concerns, each agent operates with distinct instructions, access boundaries, and tools. This multi-agent coordination makes the system highly precise, explainable, and capable of sequential problem-solving.

---

### 3. Solution
RegShield AI is an intelligent regulatory platform that streamlines the compliance lifecycle:

```
Upload Circular
      ↓
Analyze Changes
      ↓
Compare with SOPs
      ↓
Review Active Applications
      ↓
Gather Supporting Evidence
      ↓
Generate Compliance Report
```

It includes:
1.  **Circular Upload & Analysis**: Ingests new RBI circulars, extracting effective dates, affected products, and changed clauses.
2.  **Version Compare**: Identifies differences between new circulars and internal bank SOPs.
3.  **Active Application Checker**: Audits active database loan files to flag non-compliant profiles.
4.  **Evidence Gatherer**: Cross-checks files against active fraud warnings (like deepfakes and GPS location spoofing).
5.  **Compliance Report Generator**: Synthesizes findings into a signed, downloadable markdown audit report.

---

### 4. Architecture
The platform is designed with a decoupled client-server architecture:

```
Coordinator Agent (regulatory_intelligence_coordinator)
├── Circular Analysis Agent (circular_analysis_agent)
├── Policy Difference Agent (policy_diff_agent)
├── Impact Analysis Agent (impacted_cases_agent)
├── Evidence Agent (evidence_supporting_agent)
└── Recommendation Agent (recommendation_agent)
```

*   **ADK (Agent Development Kit)**: Used to define and execute the orchestrator and sub-agents.
*   **MCP (Model Context Protocol)**: Connects our agents to internal database resources.
*   **SQLite**: Serves as the repository of internal bank SOPs, circulars, customer loan files, and threat advisories.
*   **FastAPI**: Operates as the backend API server executing agent runs and streaming Server-Sent Events (SSE).
*   **Streamlit**: Provides the officer compliance portal web interface.
*   **Antigravity**: The agentic AI assistant used to code, refine, and deploy the platform.

---

### 5. ADK Implementation

| Agent | Responsibility |
| :--- | :--- |
| **Coordinator** | Orchestrates workflow, distributes queries, and compiles the final output report. |
| **Circular Analysis** | Reads the new RBI circular to extract affected products, dates, and clauses. |
| **Policy Diff** | Inspects internal SOPs and finds gaps between current bank processes and new circulars. |
| **Impact Analysis** | Evaluates active loan applications to identify specific non-compliant files. |
| **Evidence** | Retrieves relevant internal SOP guidelines and correlates active fraud advisories. |
| **Recommendation** | Synthesizes logs and produces the final actionable compliance checklist with disclaimers. |

---

### 6. MCP Server
Our custom Stdio Model Context Protocol (MCP) server exposes the bank database using the following tools:

| MCP Tool | Purpose |
| :--- | :--- |
| `search_rbi_circulars` | Searches historical and active RBI regulatory circular catalogs. |
| `search_sops` | Queries internal bank Standard Operating Procedures. |
| `list_pending_loan_applications` | Fetches active applications undergoing review including KYC logs. |
| `get_loan_application` | Retrieves deep-dive verification logs for a specific application ID. |
| `search_fraud_advisories` | Retrieves active threat alerts (e.g. GPS spoofing, deepfakes). |

---

### 7. Database
We utilize a local SQLite database (`bank_knowledge.db`) pre-populated with **55+ records per catalog table** to verify volume scalability:
*   **rbi_circulars**: Stores circular numbers, titles, issue dates, effective dates, products affected, and regulatory contents.
*   **internal_sops**: Houses bank SOP codes, product types, and step-by-step operating guidelines.
*   **fraud_advisories**: Stores threat levels, advisory codes, and attack pattern descriptions (e.g. virtual camera deepfakes).
*   **loan_applications**: Stores customer names, status, product types, requested amounts, and detailed verification/KYC logs.

---

### 8. Antigravity Workflow
The platform workflow follows a structured execution path:

```
Upload Circular ➔ Trigger Workflow ➔ Analyze ➔ Compare ➔ Impact Analysis ➔ Recommendation ➔ Compliance Report
```

**Antigravity** (Google DeepMind's agentic coding assistant) was utilized to pair-program and automate this system. Using Antigravity allowed us to:
*   Scaffold the project directory.
*   Write, test, and debug the custom MCP database connections.
*   Iterate on UI layouts in Streamlit and backend routing in FastAPI.
*   Solve concurrency, event loop, and API rate-limiting issues interactively.

---

### 9. Security
*   **Advisory-Only Recommendations**: All reports append a mandatory disclaimer stating that recommendations are advisory only and final decisions rest with authorized bank personnel.
*   **Human-in-the-Loop**: The platform provides compliance intelligence but does not automatically execute loan approvals or account closures, keeping human officers in control.
*   **Explainable Audits**: Every recommendation and flag matches specific circular numbers and SOP codes retrieved from the database, creating an explainable audit log.
*   **Secrets Safety**: API keys are managed using environment variables (`.env`) and excluded from repository commits via `.gitignore`.

---

### 10. Deployability
The application is fully containerized and Docker-ready:
*   **Docker-Ready**: A local `Dockerfile` binds FastAPI on port 8000 and Streamlit on port 8501, running both services in a single container.
*   **GCP Deployable**: Pre-configured for deployment to Google Cloud Platform **Agent Runtime** or **Cloud Run** using standard CLI commands:
    ```bash
    agents-cli scaffold enhance . --deployment-target agent_runtime
    agents-cli deploy
    ```

---

### 11. Engineering Challenges
*   **Client Event-Loop Conflicts**: Running asynchronous ADK agent runtimes directly within Streamlit's rendering threads caused dual-stack event loop DNS errors (`ClientConnectorDNSError` on `aiohttp`). We resolved this by separating concerns: running the ADK orchestrator on a backend FastAPI server and streaming logs to Streamlit via **Server-Sent Events (SSE)**.
*   **Free-Tier API Rate Limits**: The Gemini Free Tier has a strict limit of 15 Requests Per Minute (RPM) and a 20 Requests Per Day (RPD) limit per model. Looping over 25+ pending applications caused the agent to quickly hit these limits. We optimized this by expanding our MCP tools to retrieve detailed KYC data in a single batch query, reducing sequential API turns to a single turn.

---

### 12. Future Work
*   **Live Ingestion**: Integrating real-time RSS feeds from the RBI and financial regulators to automatically flag new policy drafts.
*   **Core Banking Integration**: Connecting the compliance recommendations directly to Core Banking Systems (CBS) to trigger automated transaction freezes on non-compliant accounts.
*   **Role-Based Access Control (RBAC)**: Introducing audit log tracking based on department clearance levels.

---

### 13. Conclusion
RegShield AI demonstrates how agentic AI can transform regulatory compliance from a manual, reactive process into an intelligent, proactive workflow. While demonstrated using banking regulations, the same architecture can be extended to any regulated industry where policies change frequently and operational accuracy is critical.
