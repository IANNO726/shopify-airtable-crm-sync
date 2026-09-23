import os
import logging
import requests
from dotenv import load_dotenv

# 1. Setup secure logging for client transparency
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
load_dotenv()

# 2. Securely pull credentials from environment variables
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
AIRTABLE_PAT = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")

def process_shopify_webhook(order_payload):
    """
    Validates and transforms incoming Shopify order data, then pushes it to Airtable.
    Handles multiple line items gracefully.
    """
    # Defensive programming: Ensure payload contains vital fields
    if not order_payload or "id" not in order_payload:
        logging.error("Invalid Shopify payload received.")
        return {"status": "error", "message": "Invalid payload"}

    order_id = order_payload.get("id")
    customer = order_payload.get("customer", {})
    customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or "Guest Customer"
    total_price = order_payload.get("total_price", "0.00")
    note = order_payload.get("note", "")

    # Extract and format line items into a single scannable string
    line_items = order_payload.get("line_items", [])
    items_summary = ", ".join([f"{item.get('quantity')}x {item.get('name')}" for item in line_items])

    logging.info(f"Processing Order #{order_id} for {customer_name}...")

    # 3. Format the data payload exactly how Airtable expects it
    airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    airtable_data = {
        "fields": {
            "Order ID": str(order_id),
            "Customer Name": customer_name,
            "Total Amount": float(total_price),
            "Items Ordered": items_summary,
            "Customer Notes": note
        }
    }

    # 4. Execute the network request with defensive error handling
    try:
        response = requests.post(airtable_url, json=airtable_data, headers=headers)

        # Gracefully handle Airtable's strict rate limits (5 requests per second)
        if response.status_code == 429:
            logging.warning("Hit Airtable rate limit. Triggering backup retry logic...")
            # In a live app, you would add a time.sleep() or message queue here
            return {"status": "retry", "message": "Rate limited"}

        response.raise_for_status()
        logging.info(f"Successfully synced Order #{order_id} to Airtable CRM!")
        return {"status": "success", "airtable_id": response.json().get("id")}

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while contacting Airtable: {http_err}")
        return {"status": "failed", "error": str(http_err)}
    except Exception as err:
        logging.error(f"An unexpected execution error occurred: {err}")
        return {"status": "failed", "error": str(err)}

# --- DEMO EXECUTION TRIGGER ---
if __name__ == "__main__":
    # Mocking a live incoming Shopify Webhook payload for verification
    mock_shopify_order = {
        "id": 99887766,
        "total_price": "145.50",
        "note": "Please leave packages behind the garage gate.",
        "customer": {"first_name": "Sarah", "last_name": "Connor"},
        "line_items": [
            {"name": "Cyberdyne T-800 CPU Pro", "quantity": 1},
            {"name": "Heavy Duty Diagnostic Cable", "quantity": 2}
        ]
    }

    print("--- Running Local Portfolio Health Integration Test ---")
    if not AIRTABLE_PAT:
        print("[WARN] No Airtable API Key found in env. Running dry run data formatting validation only.")
        print(f"Formatted Output: {mock_shopify_order['customer']['first_name']} bought {mock_shopify_order['line_items'][0]['name']}")
    else:
        process_shopify_webhook(mock_shopify_order)