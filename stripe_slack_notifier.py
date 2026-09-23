import os
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_payment_alert(stripe_payload):
    """
    Catches Stripe 'charge.succeeded' payloads, processes metrics, 
    and dispatches a clean, formatted alert card to Slack.
    """
    if not stripe_payload or "data" not in stripe_payload:
        logging.error("Invalid Stripe webhook payload structure.")
        return {"status": "error"}

    charge_data = stripe_payload.get("data", {}).get("object", {})
    
    # Stripe records amounts in cents (e.g., 4900 = $49.00). Convert to float.
    raw_amount = charge_data.get("amount", 0)
    formatted_amount = f"${raw_amount / 100:.2f}"
    
    customer_email = charge_data.get("billing_details", {}).get("email", "Unknown Customer")
    currency = charge_data.get("currency", "usd").upper()
    receipt_url = charge_data.get("receipt_url", "#")

    logging.info(f"Processing Stripe transaction: {formatted_amount} from {customer_email}")

    if not SLACK_WEBHOOK_URL:
        logging.warning("Slack Webhook URL missing. Executing local data extraction validation run:")
        logging.info(f"Extracted payload details successfully: {customer_email} paid {formatted_amount} {currency}")
        return {"status": "dry_run"}

    # Constructing rich Block Kit layouts for clean Slack visual notifications
    slack_blocks = {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "🔔 *New Premium Sale Notification!*"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Amount:*\n{formatted_amount} {currency}"},
                    {"type": "mrkdwn", "text": f"*Customer:*\n{customer_email}"}
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📄 View Receipt"},
                        "url": receipt_url
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=slack_blocks)
        response.raise_for_status()
        logging.info("Payment alert successfully dispatched to Slack CRM room!")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Failed to transmit payload to Slack endpoint: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    print("--- Running Stripe-to-Slack Mock Execution Diagnostic Test ---")
    mock_stripe_webhook = {
        "type": "charge.succeeded",
        "data": {
            "object": {
                "amount": 24900,  # $249.00
                "currency": "usd",
                "billing_details": {"email": "tony@starkindustries.com"},
                "receipt_url": "https://stripe.com"
            }
        }
    }
    send_slack_payment_alert(mock_stripe_webhook)
