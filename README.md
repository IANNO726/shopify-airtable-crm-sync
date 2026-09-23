# 🏘️ Real Estate CRM Automation Suite

A pair of Python integration scripts built for a real estate investor acquisition CRM and a rental property maintenance enrollment workflow — both running on Airtable as the system of record.

Built as a working prototype of the property intake, deduplication, and maintenance funnel components requested in a real client project brief for a Charlotte, NC real estate brokerage/property management company.

---

## 🛠️ Scripts in This Repo

### 1. 🏗️ Property Deduplication Engine (`property_deduper.py`)

**Problem it solves:** Investment properties arrive from multiple sources (MLS feeds, manual entry, bulk CSV imports) with inconsistently formatted addresses — "742 Evergreen Street" vs "742 Evergreen St." vs "742 Evergreen St" — that represent the same physical property. Without normalization, these create duplicate records, duplicate investor outreach, and duplicate tracking of the same deal.

**How it works:**
- Normalizes incoming street addresses: lowercases, strips punctuation, and standardizes 13 common street-suffix variants (Street→St, Terrace→Ter, Boulevard→Blvd, etc.)
- Extracts a 5-digit ZIP code from a combined "City, State, ZIP" string via regex
- Builds an MD5 fingerprint from the normalized address + ZIP
- Queries Airtable via `filterByFormula` to check if that fingerprint already exists
- Creates a new Property record only if the fingerprint is unique; otherwise logs the duplicate and skips the write, returning the existing record ID

**Sample output:**

[Step 1: Processing '742 Evergreen Street']
✅ UNIQUE PROPERTY: '742 Evergreen Street' is safe to ingest.
✅ Created new property record: recGOJCb4yXG4wH0R

[Step 2: Processing '742 Evergreen St.']
🚨 DUPLICATE DETECTED: '742 Evergreen St.' already exists in Airtable record ID: recGOJCb4yXG4wH0R
Skipped insert — duplicate of record recGOJCb4yXG4wH0R.


**Known limitation / next step:** Current matching is exact-fingerprint only. A production version would add fuzzy matching (e.g. same ZIP + high address string similarity) for near-matches that don't produce an identical fingerprint, routing those to manual review instead of auto-creating or auto-skipping.

---

### 2. 🏡 Maintenance Inspection Funnel Engine (`maintenance_funnel.py`)

**Problem it solves:** Rental property owners move through a defined outreach-to-enrollment funnel (contact → follow-up → plan approval → operational handoff) that needs to sync into Airtable so the operations team knows exactly which properties are ready to have a recurring inspection job created in Jobber — without duplicating scheduling/routing logic that Jobber already owns.

**How it works:**
- Enforces an 8-stage enrollment pipeline as a fixed set of valid stages: `Not Contacted → Outreach Sent → Follow-Up → Approved – Gold / Approved – Platinum → Needs Jobber Setup → Active in Jobber → Declined / Not Interested`
- `initiate_owner_outreach()` and `mark_follow_up_needed()` log the early-funnel contact attempts
- `process_owner_enrollment()` processes the owner's final plan choice (Gold = Annual inspections, Platinum = Every 6 Months, decline = no inspections) and automatically fast-tracks any approval straight to the `Needs Jobber Setup` action stage
- `mark_jobber_setup_complete()` PATCHes an existing record once the ops team creates the recurring job in Jobber, flipping it to `Active in Jobber` and setting the sync-confirmed flag

**Sample output:**

[Step 2: Processing Platinum Approval]
Property ID prop_991122 mapped to Stage: 'Needs Jobber Setup' (Every 6 Months Inspections)
🚀 SUCCESS: Enrolled property into database triage queue for Bruce Wayne. Record ID: recYVsoj9pT88d8aT


---

## ⚙️ Setup

1. Create a `.env` file in the project root:

AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_PERSONAL_ACCESS_TOKEN=patXXXXXXXXXXXXXX

2. In Airtable, create a Personal Access Token scoped to the specific base(s) used here, with `data.records:read` and `data.records:write` scopes only (least-privilege — no schema or workspace-wide access).
3. Ensure the base has a `Properties` table (for the dedupe engine) and a `Maintenance_Program` table (for the funnel engine) with fields matching the constants defined at the top of each script.

## 🧪 Running

```bash
python property_deduper.py
python maintenance_funnel.py
```

Each script runs a self-contained simulation against real Airtable data and logs every step — normalization, fingerprinting, API calls, and the resulting record IDs — so behavior is fully traceable without needing to open Airtable to verify what happened.

## 🧱 Architecture Notes

- Airtable is treated as the system of record; these scripts are intake/normalization layers in front of it, not a replacement for Airtable's own Interfaces/Automations.
- Field names are centralized as constants at the top of each script rather than hardcoded inline, so the scripts can be repointed at a renamed or restructured Airtable schema without touching the core logic.
- Error handling defaults to "fail safe" on network errors (dedupe check treats a failed API call as a potential duplicate to block corrupted writes) rather than "fail open."

## 🔜 Possible Extensions
- Fuzzy address matching for the dedupe engine (see limitation above)
- CSV-based bulk import mode to simulate a real MLS feed ingestion job
- Microsoft Teams/Outlook notifications when a property lands in `Needs Jobber Setup`