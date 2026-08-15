from google import genai
from google.genai import types
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import os
import pickle
from datetime import datetime

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

founder_input = {
    "IDEA_NAME": "LocalShed",
    "ONE_LINE_DESC": "A mobile app connecting micro-entrepreneurs (saree sellers, artisans, handmade goods makers) directly to customers in their neighborhoods.",
    "DETAILED_DESC": """LocalShed is a hyper-local marketplace mobile app where micro-entrepreneurs
(mostly women) can list handmade or curated products — sarees, jewelry, pottery,
embroidery, home decor — and sell directly to customers living in the same
residential complex or neighborhood. Customers download the app, browse products
from sellers in their building or within 2km radius, message sellers directly,
and arrange pickup or delivery. There are no middlemen, no e-commerce platform
taking commission from sellers. We take a 10% commission on each transaction and
offer premium seller subscriptions for 199/month. We're launching in Delhi NCR
first (Gurgaon, Noida), then expanding to Bangalore and Mumbai.""",
    "PROBLEM": """Micro-entrepreneurs in India (mostly housewives making sarees, jewelry,
pottery) currently sell through WhatsApp groups, word of mouth, or local markets.
They have no way to reach customers beyond their immediate network. On the other
side, customers want authentic, handmade products but find it hard to discover
local artisans. Existing platforms like Amazon and Flipkart take 30-50% commission,
making it unviable for small sellers. There's no platform specifically designed for
neighborhood-level commerce with direct seller-buyer connection.""",
    "PRIMARY_USERS": "Micro-entrepreneurs aged 28-55, mostly women in Gurgaon and Noida who make or sell handmade products (sarees, embroidery, jewelry, pottery, home decor). They are WhatsApp savvy but struggle with complex apps. They want to earn 10-30K/month from home without leaving their families or paying high commissions to marketplace platforms",
    "SECONDARY_USERS": "Yes. Secondary user: Customers aged 25-45 living in urban residential complexes (Gurgaon, Noida) who actively seek authentic, handmade products, support local artisans, and prefer direct seller-buyer relationships. They're willing to pay premium prices for quality and authenticity.",
    "MONETIZATION": "10% commission on every transaction. Additionally, premium seller subscription at 199/month that gives sellers featured listing, priority visibility in search, and analytics dashboard.",
    "COMPETITORS": "Direct: WhatsApp groups, local artisan communities, Instagram sellers. Indirect: Amazon, Flipkart (high commission), Etsy, Meesho.",
    "DIFFERENTIATOR": "Hyper-local, neighborhood-level transactions. Direct seller-buyer relationships. Built specifically for Indian micro-entrepreneurs with Hindi/regional language support. No shipping complexity — everything is local pickup or same-area delivery.",
    "PLATFORM": "Both mobile app (iOS + Android) + web dashboard",
    "STACK_PREFERENCE": "No strong preference, whatever works best",
    "INTEGRATIONS": "Payments (UPI via Razorpay), Google Maps, OTP login, Push notifications, In-app messaging, Location-based search",
    "CITIES": "Gurgaon and Noida first (Delhi NCR), then Bangalore and Mumbai",
    "BUDGET": "2-5 lakh",
    "TIMELINE": "3-6 months for MVP"
}


def load_prompt(founder_data):
    with open("prompts/gemini_prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    for key, value in founder_data.items():
        prompt = prompt.replace(f"{{{key}}}", str(value).strip())
    return prompt


def call_gemini(prompt):
    print("Calling Gemini Flash...")
    print("This may take 30-60 seconds...\n")
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8192,
        )
    )
    return response.text


def parse_and_save(raw_output, idea_name):
    cleaned = raw_output.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        print("JSON parsed successfully!\n")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        folder = f"clients/{idea_name.replace(' ', '_')}"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/raw_output.txt", "w", encoding="utf-8") as f:
            f.write(raw_output)
        print(f"Raw output saved to {folder}/raw_output.txt")
        return None

    folder = f"clients/{idea_name.replace(' ', '_')}"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/spec_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Spec saved to: {filename}")
    return data


def get_google_services():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("oauth_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    return docs_service, drive_service


def format_for_gdocs(value):
    """
    Converts any Gemini JSON value into clean, human-readable text
    for Google Docs replaceAllText (which only accepts flat strings).

    Rules:
    - None              → empty string
    - Plain string      → returned as-is
    - Flat list         → bullet list joined by newlines  (• item)
    - List of dicts     → each dict becomes a labelled block, separated by blank lines
                          Nested lists inside a dict become indented bullets (  - item)
    - Plain dict        → Key: Value lines
    """
    if value is None:
        return ""

    # ── Plain string ──────────────────────────────────────────────
    if isinstance(value, str):
        return value

    # ── List ──────────────────────────────────────────────────────
    if isinstance(value, list):
        # List of dicts (e.g. WIREFRAME_DESCRIPTIONS, DATA_MODELS, API_ENDPOINTS)
        if value and isinstance(value[0], dict):
            blocks = []
            for item in value:
                lines = []
                for k, v in item.items():
                    if isinstance(v, list):
                        # Nested list → indented bullets
                        sub_bullets = "\n".join(f"   - {sub}" for sub in v)
                        lines.append(f"{k}:\n{sub_bullets}")
                    else:
                        lines.append(f"{k}: {v}")
                blocks.append("\n".join(lines))
            return "\n\n".join(blocks)

        # Flat list of strings (e.g. MVP_FEATURES, COMPLIANCE_REQUIREMENTS)
        return "\n".join(f"• {item}" for item in value)

    # ── Plain dict (e.g. a single object) ─────────────────────────
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if isinstance(v, list):
                sub_bullets = "\n".join(f"   - {sub}" for sub in v)
                lines.append(f"{k}:\n{sub_bullets}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)

    # ── Fallback (numbers, booleans, etc.) ────────────────────────
    return str(value)


def fill_template_and_export(data, idea_name):
    # Read IDs fresh inside the function — no global scope issues
    template_doc_id = os.environ.get("TEMPLATE_DOC_ID", "").strip()
    shared_drive_id = os.environ.get("SHARED_DRIVE_ID", "").strip()

    print(f"Using TEMPLATE_DOC_ID: {template_doc_id}")
    print(f"Using SHARED_DRIVE_ID: {shared_drive_id}")

    if not template_doc_id:
        print("ERROR: TEMPLATE_DOC_ID is empty. Check your .env file.")
        return None

    docs_service, drive_service = get_google_services()

    folder = f"clients/{idea_name.replace(' ', '_')}"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    new_doc_id = None
    try:
        # Copy template into the SpecForge folder
        copy_title = f"{idea_name} - Spec Report - {timestamp}"
        copy_body = {"name": copy_title}

        copied_file = drive_service.files().copy(
            fileId=template_doc_id,
            body=copy_body,
        ).execute()
        new_doc_id = copied_file["id"]
        print(f"Template copied (temp ID: {new_doc_id})")

        # Replace all placeholders
        requests = []
        for key, value in data.items():
            placeholder = "{{" + key + "}}"
            replacement_text = format_for_gdocs(value)   # ← was: str(value)
            requests.append({
                "replaceAllText": {
                    "containsText": {"text": placeholder, "matchCase": True},
                    "replaceText": replacement_text,
                }
            })

        docs_service.documents().batchUpdate(
            documentId=new_doc_id, body={"requests": requests}
        ).execute()
        print(f"Placeholders replaced ({len(requests)} fields)")

        # Export as PDF
        pdf_bytes = drive_service.files().export(
            fileId=new_doc_id, mimeType="application/pdf"
        ).execute()

        pdf_path = f"{folder}/{idea_name.replace(' ', '_')}_{timestamp}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"\nPDF saved to: {pdf_path}")

        # Delete temp doc
        drive_service.files().delete(fileId=new_doc_id, supportsAllDrives=True).execute()
        print("Temp doc deleted from Drive")

        return pdf_path

    except HttpError as e:
        print(f"\nGoogle API error: {e}\n")
        if new_doc_id:
            try:
                drive_service.files().delete(fileId=new_doc_id, supportsAllDrives=True).execute()
            except:
                pass
        return None


def print_summary(data):
    if not data:
        return
    print("\n" + "="*60)
    print("SPEC GENERATION SUMMARY")
    print("="*60)
    print(f"Product:  {data.get('PRODUCT_NAME', 'N/A')}")
    print(f"Persona 1: {data.get('PERSONA_1_NAME', 'N/A')}")
    print(f"Persona 2: {data.get('PERSONA_2_NAME', 'N/A')}")
    print(f"Persona 3: {data.get('PERSONA_3_NAME', 'N/A')}")
    print(f"Budget:   {data.get('TOTAL_FIRST_YEAR_COST', 'N/A')}")
    print(f"Timeline: {data.get('TIMELINE_MONTHS', 'N/A')} months")
    sections = ["EXEC_SUMMARY","USER_STORIES_FULL","MVP_FEATURES",
                "WIREFRAME_DESCRIPTIONS","DATA_MODELS","API_ENDPOINTS",
                "HIRING_RECOMMENDATION","COMPLIANCE_REQUIREMENTS"]
    for s in sections:
        print(f"  {'✓' if data.get(s) else '✗ MISSING'} {s}")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("SPECFORGE - AI Spec Generator")
    print("="*60)
    print(f"Generating spec for: {founder_input['IDEA_NAME']}\n")

    prompt = load_prompt(founder_input)
    raw_output = call_gemini(prompt)
    data = parse_and_save(raw_output, founder_input["IDEA_NAME"])
    print_summary(data)

    if data:
        fill_template_and_export(data, founder_input["IDEA_NAME"])
