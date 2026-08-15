# Specforge — Spec Document PDF Generator

Automatically generate professional software specification documents from a simple Google Form. Perfect for non-technical founders and product managers who need detailed spec documents without writing them manually.

## Problem Solved

Non-technical founders struggle to create detailed specification documents. They lack the technical knowledge to write out user personas, feature lists, data models, API endpoints, and tech stack recommendations. Specforge automates this entire process.

## How It Works

1. **Founder fills a Google Form** with basic project details (idea name, problem statement, target users, key features, budget, timeline expectations)
2. **Python script reads form responses** from Google Sheets via Forms API
3. **Gemini API generates all 11 sections** based on the input
4. **PDF is generated** with professional formatting
5. **Output is delivered** to the founder

## Features

The generated spec document includes:

- **Executive Summary** — High-level overview of the project
- **User Personas** — Target users and their characteristics
- **User Stories** — Feature requirements in user story format
- **Feature List** — Detailed breakdown of all features
- **Wireframe Descriptions** — Basic layout descriptions for key screens
- **Data Models** — Database schema and relationships
- **API Endpoint List** — All required API endpoints with details
- **Tech Stack Recommendation** — Suggested technology stack for building
- **Cost & Timeline Estimate** — Development cost and timeline breakdown
- **Hiring Recommendations** — Team composition needed to build
- **Risk and Compliance** — Potential risks and compliance considerations

## Tech Stack

- **Python** — Core scripting language
- **FastAPI** — Web framework (optional, for API wrapper)
- **Google Forms API** — Read form responses
- **Google Sheets API** — Access response data
- **Gemini API** — AI-powered content generation
- **Google Drive API** — Store and manage PDFs
- **fpdf2** — PDF generation and formatting
- **OAuth 2.0** — Secure Google account authentication

## Project Setup

### Prerequisites
- Python 3.9+
- Google Cloud Project with APIs enabled (Forms, Sheets, Drive, Gemini)
- Service account credentials (for automation)
- Gemini API key

### Installation

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client google-generativeai fpdf2 python-dotenv
```

### Configuration

1. Set up Google Cloud Project and enable required APIs
2. Create service account and download credentials JSON
3. Create `.env` file with:
   ```
   GEMINI_API_KEY=your_api_key
   GOOGLE_FORMS_ID=your_form_id
   GOOGLE_SHEET_ID=your_sheet_id
   CREDENTIALS_FILE=path_to_credentials.json
   ```

## Key Learnings

- **Google APIs**: OAuth 2.0 flow, service accounts, Forms/Sheets/Drive API integration
- **LLM Integration**: Prompt engineering, structured output from Gemini API
- **Document Generation**: PDF creation with fpdf2, formatting, multi-section documents
- **API Orchestration**: Connecting multiple Google APIs in a single pipeline

## Use Cases

- Startup founders need a spec to pitch investors
- Product managers documenting feature requirements
- Development teams getting clarity on project scope
- Clients providing specs to development agencies

## Future Improvements

- Web interface for form submission
- Multiple PDF template styles
- Webhook integration for automatic triggering
- Revision/iteration workflow
- Integration with project management tools (Asana, Jira)

## Author

Shivraj | 2nd Year B.Tech CSE/AIML | College of Engineering, Pune
