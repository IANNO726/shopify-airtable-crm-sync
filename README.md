# ⚡ Enterprise AI Workflow & API Automation Suite

A production-grade collection of cloud-native automation engines designed to eliminate manual business overhead, streamline operational communication, and integrate artificial intelligence into standard corporate data pipelines.

This suite provides businesses with self-healing, secure, and highly scalable data connectivity blueprints.

---

## 🛠️ The Automation Portfolio Suite

The repository contains three distinct, production-ready integration engines:

### 1. 🛒 Shopify to Airtable CRM Sync (`sync_agent.py`)
*   **Business Impact:** Synchronizes real-time incoming Shopify e-commerce webhooks into an Airtable CRM database.
*   **Technical Edge:** Natively handles multi-item array payload flattening and integrates a custom watch-dog handler to intercept and bypass Airtable's strict 5 requests-per-second (`HTTP 429`) rate limits without data loss.

### 💳 2. Stripe-to-Slack Revenue Notifier (`stripe_slack_notifier.py`)
*   **Business Impact:** Tracks live Stripe transaction pipelines and instantly formats financial metrics into styled team notifications.
*   **Technical Edge:** Automatically reformats processing payloads from fractional integers (cents) to clean localized currency data fields, delivering custom visual cards via Slack's block framework.

### 🧠 3. Intelligent AI Lead Scoring Engine (`ai_lead_scorer.py`)
*   **Business Impact:** Intercepts incoming corporate website contact forms and automatically prioritizes them for sales teams.
*   **Technical Edge:** Leverages the official Google GenAI SDK to pass incoming data securely to the `gemini-2.5-flash` model. It accurately scores incoming clients (`HIGH`, `MEDIUM`, or `LOW`) based on business scale and textual buying urgency.

---

## 📊 Suite Architecture

[ Business Event Triggers ]│├──► (Shopify Order) ────► [ sync_agent.py ] ──────────► [ Airtable CRM ]│├──► (Stripe Payment) ───► [ stripe_slack_notifier.py ] ► [ Slack Operations ]│└──► (Website Lead) ─────► [ ai_lead_scorer.py ] ───────► [ Gemini AI Engine ]

---

## ⚙️ Environment Configuration

Set up a `.env` file in your root directory to manage enterprise tokens securely for Airtable, Slack, and Google GenAI.

---

## 🧪 Operational Verification Diagnostics

Run individual script commands (such as `python sync_agent.py`) to execute isolated built-in health checks and validate integration functionalities before production deployment.

---

## 💼 Enterprise Customization Services
The modular architecture supports extensions like custom database integration (PostgreSQL, MongoDB), cross-platform webhooks, and AI spam filters.
🚀 Update Your Online PortfolioRun standard git commands (git add, git commit, git push origin main) via your terminal to publish the updated documentation live to your repository and finalize your portfolio display.