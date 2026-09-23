import os
import re
import csv
import logging
import requests
import hashlib
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[⚙️ DEDUPE ENGINE] %(asctime)s - %(message)s')
load_dotenv()

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_PAT = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
TABLE_NAME = "Properties"

# ---- Field name config: must match your Airtable table exactly ----
FIELD_ADDRESS = "Street Address"
FIELD_CITY_STATE_ZIP = "City, State, Zip Code"
FIELD_HASH = "Property Hash"
FIELD_SOURCE = "Source"
FIELD_STATUS = "Status"

# ---- Street suffix normalization map ----
SUFFIX_REPLACEMENTS = {
    " street": " st",
    " avenue": " ave",
    " road": " rd",
    " boulevard": " blvd",
    " drive": " dr",
    " court": " ct",
    " lane": " ln",
    " terrace": " ter",
    " place": " pl",
    " circle": " cir",
    " highway": " hwy",
    " parkway": " pkwy",
    " trail": " trl",
    " square": " sq",
    " loop": " loop"
}


def standardize_address(address_string):
    """
    Normalizes real estate address strings to ensure consistent matching metrics.
    Converts text to lowercase, strips punctuation, and standardizes street suffixes.
    """
    if not address_string:
        return ""

    clean = address_string.lower().strip()
    clean = clean.replace(".", "").replace(",", "")

    for word, replacement in SUFFIX_REPLACEMENTS.items():
        if clean.endswith(word) or word + " " in clean:
            clean = clean.replace(word, replacement)

    return clean.strip()


def extract_zip(city_state_zip_string):
    """
    Pulls a 5-digit ZIP code out of a combined 'City, State, Zip' string.
    Falls back to empty string if no match is found.
    """
    if not city_state_zip_string:
        return ""
    match = re.search(r"\b(\d{5})\b", city_state_zip_string)
    return match.group(1) if match else ""


def build_fingerprint(street_address, zip_code):
    normalized_address = standardize_address(street_address)
    normalized_zip = str(zip_code).strip()
    unique_string = f"{normalized_address}-{normalized_zip}"
    return hashlib.md5(unique_string.encode()).hexdigest()


def check_for_duplicate_property(street_address, zip_code):
    """
    Queries Airtable to see if this specific property key already exists.
    Returns (is_duplicate: bool, fingerprint: str, existing_record_id: str|None)
    """
    property_fingerprint = build_fingerprint(street_address, zip_code)
    logging.info(f"Checking uniqueness for: '{street_address}' -> Hash: {property_fingerprint}")

    if not AIRTABLE_PAT:
        logging.warning("Dry-run mode: Missing API keys. Assuming property is unique.")
        return False, property_fingerprint, None

    airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_PAT}"}
    params = {
        "filterByFormula": f"{{{FIELD_HASH}}} = '{property_fingerprint}'"
    }

    try:
        response = requests.get(airtable_url, headers=headers, params=params)
        response.raise_for_status()
        records = response.json().get("records", [])

        if len(records) > 0:
            existing_id = records[0]["id"]
            logging.warning(f"🚨 DUPLICATE DETECTED: '{street_address}' already exists in Airtable record ID: {existing_id}")
            return True, property_fingerprint, existing_id

        logging.info(f"✅ UNIQUE PROPERTY: '{street_address}' is safe to ingest.")
        return False, property_fingerprint, None

    except Exception as e:
        logging.error(f"Failed to query database validation layers: {e}")
        return True, property_fingerprint, None  # Err on the side of safety to block corrupted writes


def create_property_record(street_address, city_state_zip, property_hash, source="Manual Entry"):
    """
    Creates a new Property record in Airtable after uniqueness has been confirmed.
    """
    if not AIRTABLE_PAT:
        logging.warning("Dry-run mode: Missing API keys. Skipping record creation.")
        return None

    airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }
    payload = {
        "fields": {
            FIELD_ADDRESS: street_address,
            FIELD_CITY_STATE_ZIP: city_state_zip,
            FIELD_HASH: property_hash,
            FIELD_SOURCE: source,
            FIELD_STATUS: "New"
        }
    }

    try:
        response = requests.post(airtable_url, headers=headers, json=payload)
        response.raise_for_status()
        record = response.json()
        logging.info(f"✅ Created new property record: {record['id']}")
        return record
    except Exception as e:
        logging.error(f"Failed to create property record: {e}")
        return None


def process_property_feed(address, city_state_zip, source="Manual Entry"):
    """
    End-to-end intake: dedupe check -> create record if unique -> skip if duplicate.
    """
    zip_code = extract_zip(city_state_zip)
    is_dup, fingerprint, existing_id = check_for_duplicate_property(address, zip_code)

    if is_dup:
        logging.info(f"Skipped insert — duplicate of record {existing_id}.")
        return {"status": "duplicate", "record_id": existing_id}

    record = create_property_record(address, city_state_zip, fingerprint, source)
    return {"status": "created", "record": record}


if __name__ == "__main__":
    print("\n--- 🏗️ RUNNING ENTERPRISE CRM PIPELINE SIMULATION ---")

    # Simulate an automated bulk-import feed. In production this would come from
    # an MLS API response; here we hardcode it to mimic that intake path.
    # Note: Step 1 and Step 2 represent the SAME physical property, written
    # differently by two different feeds — this is exactly what the dedupe
    # engine exists to catch.
    incoming_feed = [
        {"address": "742 Evergreen Street", "city_state_zip": "Charlotte, NC 28202", "source": "MLS Feed"},
        {"address": "742 Evergreen St.", "city_state_zip": "Charlotte, NC 28202", "source": "Bulk Import"},  # duplicate of above
        {"address": "16 Willowbrook Ln", "city_state_zip": "Austin, TX 78745", "source": "Manual Entry"},
    ]

    for i, prop in enumerate(incoming_feed, start=1):
        print(f"\n[Step {i}: Processing '{prop['address']}']")
        result = process_property_feed(prop["address"], prop["city_state_zip"], prop["source"])
        print(f"   -> Result: {result['status']}")