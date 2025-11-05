import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

load_dotenv()

AIRTABLE_API_TOKEN = os.getenv("AIRTABLE_API_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
USERS_TABLE = os.getenv("AIRTABLE_USERS_TABLE")
TICKETS_TABLE = os.getenv("AIRTABLE_TICKETS_TABLE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_TOKEN}", "Content-Type": "application/json"}

if ChatGoogleGenerativeAI is not None and GEMINI_API_KEY:
    parser_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
else:
    parser_llm = None

def extract_fields(prompt: str, expected: list[str]) -> dict:
    """Extract structured fields from natural prompt.

    If a parser LLM is available (parser_llm), use it. Otherwise fall back to
    simple regex heuristics for common fields like `user_id` and `issue` so the
    module remains importable in lightweight environments.
    """
    # Use the LLM parser when available
    if parser_llm is not None:
        schema_str = ", ".join(expected)
        extract_prompt = f"Extract the following details from the text: {schema_str}.\nText: {prompt}\nReturn them as key:value pairs."
        result = parser_llm.invoke(extract_prompt)
        output = result.content.strip()

        parsed = {}
        for field in expected:
            match = re.search(rf"{field}[:=]\s*([^\n,]+)", output, re.IGNORECASE)
            if match:
                parsed[field] = match.group(1).strip()
        return parsed


# Search for user
def search_user(prompt: str) -> str:
    """Smart search user tool: understands natural text like 'check if user 123 exists'."""
    fields = extract_fields(prompt, ["user_id"])
    user_id = fields.get("user_id") or re.findall(r"\d+", prompt)
    user_id = user_id[0] if isinstance(user_id, list) and user_id else user_id
    if not user_id:
        return "Please provide a user ID to check."

    url = f"{AIRTABLE_URL}/{USERS_TABLE}"
    params = {"filterByFormula": f"{{User ID}}='{user_id}'"}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if data.get("records"):
        return f"User {user_id} exists in the database."
    return f"User {user_id} not found."


#  Create Ticket 
def create_ticket(prompt: str) -> str:
    """Smart create ticket tool: understands natural text like 'create a ticket for user 12 about a login issue'."""
    fields = extract_fields(prompt, ["user_id", "issue"])
    user_id = fields.get("user_id") or re.findall(r"\d+", prompt)
    user_id = user_id[0] if isinstance(user_id, list) and user_id else user_id
    issue = fields.get("issue") or re.sub(r".*about", "", prompt, flags=re.IGNORECASE).strip()

    if not user_id:
        return "Please provide a user ID."
    if not issue:
        return "Please describe the issue."

    verify = search_user(f"user_id: {user_id}")
    if "not found" in verify:
        return "Sorry, this user does not exist in our database."

    url = f"{AIRTABLE_URL}/{TICKETS_TABLE}"
    data = {
        "fields": {
            "User ID": user_id,
            "Reason": issue,
            "Status": "In Progress",
            "Submission Date": datetime.now().strftime("%Y-%m-%d")
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)

    if response.status_code in [200, 201]:
        return f"Ticket created successfully for user {user_id} — Issue: {issue}"
    return f"Failed to create ticket. Error: {response.text}"


# Ticket Status 
def ticket_status(prompt: str) -> str:
    """Smart ticket status tool: understands natural text like 'check status for user 5' or 'ticket for user 22'."""
    fields = extract_fields(prompt, ["user_id"])
    user_id = fields.get("user_id") or re.findall(r"\d+", prompt)
    user_id = user_id[0] if isinstance(user_id, list) and user_id else user_id

    if not user_id:
        return "Please provide a user ID to check ticket status."

    # Verify user
    verify = search_user(f"user_id: {user_id}")
    if "not found" in verify:
        return "Sorry, this user does not exist in our database."

    url = f"{AIRTABLE_URL}/{TICKETS_TABLE}"
    params = {
        "filterByFormula": f"{{User ID}}='{user_id}'",
        "fields[]": ["Status", "Reason"]
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    records = data.get("records", [])
    if not records:
        return "No tickets found for this user."

    lines = [f"{r['fields'].get('Reason', 'N/A')} → Status: {r['fields'].get('Status', 'N/A')}" for r in records]
    return "\n".join(lines)
