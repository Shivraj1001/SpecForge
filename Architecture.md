SPECFORGE — AI Spec Generator
==============================

FOLDER STRUCTURE:
specforge/
  main.py              ← Run this
  requirements.txt     ← Install these
  prompts/
    gemini_prompt.txt  ← The AI prompt (don't touch unless tuning)
  clients/
    TiffinConnect/     ← One folder per customer, auto-created
      spec_20250502.json
  outputs/             ← For future use

SETUP (Do this once):

1. Get Gemini API Key:
   - Go to https://aistudio.google.com/
   - Click "Get API Key"
   - Copy the key

2. Add your key to main.py:
   - Open main.py
   - Find: GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
   - Replace with your actual key

3. Install dependencies:
   pip install -r requirements.txt

HOW TO USE (For each customer):

1. Open main.py
2. Fill in the founder_input dictionary with the customer's form answers
3. Run: python main.py
4. Check clients/[IdeaName]/spec_TIMESTAMP.json for the output
5. Open your Google Docs template
6. Use Ctrl+H to Find & Replace each {{PLACEHOLDER}} with the JSON value
7. Export as PDF
8. Send to customer

TROUBLESHOOTING:

- If JSON parse fails: check clients/[name]/raw_output.txt for the raw Gemini output
- If output is too generic: add more detail to the founder's form answers
- If sections are missing: re-run the script (Gemini is non-deterministic)
- If API quota exceeded: wait 1 minute and retry (free tier limit)

COST ESTIMATE (Free tier):
- Gemini Flash free tier: 15 requests/minute, 1500 requests/day
- Each spec generation = 1 request
- You can generate 1500 specs/day for free
- More than enough for current volume

NEXT STEPS (When you have 15+ customers):
- Automate form → script via Google Forms webhook
- Add Claude Haiku for polish pass
- Add HTML template for auto-PDF generation