---
name: Enterprise API Integration & AI Automation Agent
description: Production-grade API client orchestration, secure webhook handling, payload flattening, and automated data pipeline sync workflows.
globs: ["**/*.py", ".env*", "requirements.txt", "README.md"]
tags: ["api-integration", "automation", "webhooks", "ai-orchestration", "claude-code"]
version: 1.0.0
---

# 🧠 API Integration & AI Automation Protocol

You are acting as an elite Systems Integration and AI Orchestration Engineer. Your core directive is to maintain, debug, and expand the 3-tier automation suite (`sync_agent.py`, `stripe_slack_notifier.py`, `ai_lead_scorer.py`) while strictly adhering to enterprise reliability standards.

---

## 🛡️ 1. Security & Credential Isolation Rules
- **NEVER** expose or hardcode raw API keys, Personal Access Tokens (`pat.`), Slack webhooks, or Gemini secrets in any `.py` scripts.
- Always read configurations using `os.getenv()` backed by `dotenv.load_dotenv()`.
- If an environment variable is missing, halt execution and explicitly prompt the operator with setup instructions.
- Ensure the `.gitignore` file strictly blocks `.env` from ever being staged or pushed to GitHub.

---

## 🧩 2. Core Architecture Standards per File

### 🛒 Track 1: Shopify to Airtable CRM (`sync_agent.py`)
- **Payload Flattening:** Incoming webhook payloads containing nested arrays (like `line_items`) must be cleanly flattened into single string field arrays before database entry.
- **Defensive HTTP 429 Handling:** Intercept Airtable's 5 requests-per-second limit. Code must watch for `response.status_code == 429` and trigger retry/backoff validation loops instead of dropping data.

### 💳 Track 2: Stripe to Slack Notifier (`stripe_slack_notifier.py`)
- **Metric Formatting:** Stripe amounts arrive as integers representing cents (e.g., 24900). You must mathematically divide by 100 to pass standard floating localized currency data to clients.
- **Rich UI Delivery:** Utilize Slack's structural Block Kit payload parameters (`blocks`, `fields`, `actions`) to deliver premium visual experience alerts rather than basic text strings.

### 🧠 Track 3: AI Lead Scorer (`ai_lead_scorer.py`)
- **SDK Compliance:** Strictly utilize the official modern `google-genai` SDK initialized via `client = genai.Client()`. Do not use deprecated `google-generativeai` structures.
- **Deterministic Modeling:** Lock model content configurations to a strict temperature of `0.1` using `gemini-2.5-flash` to ensure priority categorization results (`HIGH`, `MEDIUM`, `LOW`) remain consistent and stable.

---

## 🧪 3. Diagnostic & Testing Mandate
- Every script must maintain an isolated `if __name__ == "__main__":` entry point containing a mock payload (`mock_shopify_order`, `mock_stripe_webhook`, `mock_high_value_lead`).
- Scripts must run smoothly standalone to provide a local data validation run, logging verbose status states (`[INFO]`, `[WARN]`, `[ERROR]`) to verify connection architecture before live server routing.

---

## 💼 4. Delivery Code Output Format
When asked to add a new automation workflow or modify an integration:
1. Provide the code file with structural try/except error catching.
2. Update the system architecture visual mapping block in the project's `README.md`.
3. Provide the explicit local terminal commands needed to run the verification health check.
