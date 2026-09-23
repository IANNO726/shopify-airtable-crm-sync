import os
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[🔧 MAINTENANCE ENGINE] %(asctime)s - %(message)s')
load_dotenv()

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_PAT = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
TABLE_NAME = "Maintenance_Program"

# Establish the strict 8-stage operational matrix required by the client
VALID_STAGES = [
    "Not Contacted", "Outreach Sent", "Follow-Up",
    "Approved – Gold", "Approved – Platinum",
    "Needs Jobber Setup", "Active in Jobber", "Declined / Not Interested"
]


def _push_to_airtable(fields, action_description):
    """
    Shared helper: POSTs a fields payload to the Maintenance_Program table.
    """
    if not AIRTABLE_PAT:
        logging.warning("Dry-run validation: Skipping live network push.")
        return {"status": "dry_run", "fields": fields}

    airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }
    payload = {"fields": fields}

    try:
        response = requests.post(airtable_url, json=payload, headers=headers)

        if response.status_code == 404:
            logging.error(f"Table '{TABLE_NAME}' not found. Please verify the table name in Airtable.")
            return {"status": "table_missing"}

        if response.status_code == 422:
            logging.error(f"Field/value rejected by Airtable (422): {response.text}")
            return {"status": "invalid_fields", "error": response.text}

        response.raise_for_status()
        record_id = response.json().get("id")
        logging.info(f"🚀 SUCCESS: {action_description}. Record ID: {record_id}")
        return {"status": "success", "record_id": record_id}
    except Exception as e:
        logging.error(f"Failed to execute Airtable push: {e}")
        return {"status": "failed", "error": str(e)}


def initiate_owner_outreach(property_id, owner_name, zip_code):
    """
    Stage 1 of the funnel: logs a new property/owner as contacted,
    setting the enrollment stage to 'Outreach Sent'.
    """
    logging.info(f"Logging outreach for owner: {owner_name} (Property {property_id})...")

    fields = {
        "Property ID": property_id,
        "Owner Name": owner_name,
        "ZIP Code": str(zip_code).strip(),
        "Enrollment Stage": "Outreach Sent",
        "Inspection Frequency": "None",
        "Jobber Sync Confirmed": "No"
    }

    return _push_to_airtable(fields, f"Logged outreach for {owner_name}")


def mark_follow_up_needed(property_id, owner_name, zip_code):
    """
    Stage 2 of the funnel: owner hasn't responded yet, so the property
    moves into the 'Follow-Up' stage for a second outreach attempt.
    """
    logging.info(f"Marking follow-up needed for owner: {owner_name} (Property {property_id})...")

    fields = {
        "Property ID": property_id,
        "Owner Name": owner_name,
        "ZIP Code": str(zip_code).strip(),
        "Enrollment Stage": "Follow-Up",
        "Inspection Frequency": "None",
        "Jobber Sync Confirmed": "No"
    }

    return _push_to_airtable(fields, f"Marked follow-up for {owner_name}")


def process_owner_enrollment(property_id, owner_name, zip_code, chosen_plan):
    """
    Final stage of the funnel: processes an inbound owner form submission
    (approval or decline), maps plan frequencies, and transitions approved
    properties straight to the 'Needs Jobber Setup' action queue.
    """
    logging.info(f"Processing enrollment form submission for owner: {owner_name}...")

    if chosen_plan == "Gold":
        frequency = "Annual"
        target_stage = "Needs Jobber Setup"
    elif chosen_plan == "Platinum":
        frequency = "Every 6 Months"
        target_stage = "Needs Jobber Setup"
    else:
        frequency = "None"
        target_stage = "Declined / Not Interested"

    logging.info(f"Property ID {property_id} mapped to Stage: '{target_stage}' ({frequency} Inspections)")

    fields = {
        "Property ID": property_id,
        "Owner Name": owner_name,
        "ZIP Code": str(zip_code).strip(),
        "Enrollment Stage": target_stage,
        "Inspection Frequency": frequency,
        "Jobber Sync Confirmed": "No"
    }

    return _push_to_airtable(fields, f"Enrolled property into database triage queue for {owner_name}")


def mark_jobber_setup_complete(record_id):
    """
    Operational step: once the ops team creates the recurring job in Jobber,
    this flips the record's status to 'Active in Jobber' and confirms sync.
    Requires the Airtable record_id returned from an earlier push.
    """
    if not AIRTABLE_PAT:
        logging.warning("Dry-run validation: Skipping live network push.")
        return {"status": "dry_run"}

    airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }
    payload = {
        "fields": {
            "Enrollment Stage": "Active in Jobber",
            "Jobber Sync Confirmed": "Yes"
        }
    }

    try:
        response = requests.patch(airtable_url, json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"🔄 Record {record_id} marked Active in Jobber.")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Failed to update Jobber sync status: {e}")
        return {"status": "failed", "error": str(e)}


if __name__ == "__main__":
    print("\n--- 🏡 RUNNING RENTAL MAINTENANCE WORKFLOW INGESTION ---")

    # Simulation 1: New property enters the funnel — initial outreach
    print("\n[Step 1: Initial Owner Outreach]")
    initiate_owner_outreach(
        property_id="prop_778899",
        owner_name="Clark Kent",
        zip_code="28204"
    )

    # Simulation 2: Owner approves a premium Platinum tier plan
    print("\n[Step 2: Processing Platinum Approval]")
    process_owner_enrollment(
        property_id="prop_991122",
        owner_name="Bruce Wayne",
        zip_code="28205",
        chosen_plan="Platinum"
    )

    # Simulation 3: Owner declines the service offering
    print("\n[Step 3: Processing Opt-Out Submission]")
    process_owner_enrollment(
        property_id="prop_445566",
        owner_name="Lex Luthor",
        zip_code="28202",
        chosen_plan="Declined"
    )