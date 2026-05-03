# ConstructProcure AI
**Multi-Agent Supply Chain Management System for the Construction Domain**

ConstructProcure AI is a stateful, multi-agent AI system designed to automate the construction procurement lifecycle. It replaces manual supplier outreach and quotation evaluation by orchestrating a network of specialized AI agents to discover suppliers, extract data from unstructured documents, map referral networks, and calculate trust scores based on deterministic math.

---

## 🏗️ System Architecture

The system utilizes a **Supervisor-Worker** pattern orchestrated by LangGraph. All agents communicate by reading and updating a shared `ProcurementState` object.

### The 7-Agent Network:
1. **Supervisor Agent (Orchestrator):** Receives the initial requirement, routes tasks to worker agents, and manages conditional graph transitions.
2. **Discovery Agent (Sourcing):** Queries the database to find known suppliers matching the required material category.
3. **Communication Agent (Outreach):** Handles external communication, sends quotation requests, and monitors for replies.
4. **Extraction Agent (Data Parsing):** Processes raw emails and PDFs (using Instructor + Groq), forcing the LLM to output strictly validated JSON (`Quotation` schemas).
5. **Graph Builder Agent (Networking):** Scans text for supplier mentions, updates an in-memory NetworkX graph, and calculates PageRank for referral quality.
6. **Scoring Agent (Evaluation):** Applies Multi-Criteria Decision Analysis (MCDA) to rank suppliers based on response speed, price competitiveness, quote completeness, and referral quality.
7. **Analyst Agent (Reporting):** Translates the mathematical rankings into a final, human-readable recommendation report.

---

## 💻 Technology Stack (Local MVP)

* **Orchestration:** LangGraph (StateGraph & SqliteSaver)
* **LLM Backend:** Groq (`llama-3.3-70b-versatile`)
* **Structured Output:** Instructor + Pydantic v2
* **Document Parsing:** pdfplumber / LlamaParse
* **Database & Memory:** SQLite + SQLAlchemy
* **Network Graph:** NetworkX
* **API Framework:** FastAPI

---

## 🚀 Setup & Installation

### 1. Initialize Environment
```bash
python -m venv venv
```
python -m app.agents.extraction
```