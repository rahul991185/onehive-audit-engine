# OneHive Technologies — Digital Presence Intelligence Engine
> **"Give Away The Diagnosis. Sell The Treatment."**  
> Better Presence. Bigger Possibilities. • Build. Automate. Grow.

An automated sales-intelligence engine and lead-generation system for OneHive Technologies. Given a single business URL (Google Maps, Website, Instagram, or Facebook), the engine automatically conducts real-time multi-source research, verifies business identity, runs deterministic scoring across 6 dimensions, isolates the #1 growth bottleneck, and produces the complete **OneHive Digital Growth Pack**.

---

## 1. What The Product Produces

Every successful audit automatically generates the complete **OneHive Digital Growth Pack**:

1. **5-Page Consulting PDF Report (`report.pdf`)**:
   - Strictly 5 pages (A4 portrait) using the approved OneHive yellow/black consulting design system.
   - Embeds an actual visual preview of the personalized website concept directly on Page 4.
   - Zero hallucinated statistics (no "73%", "lost revenue", or "dominant #1").
2. **Personalized Website Concept Teaser**:
   - Rendered at **Desktop (1440px)** and **Mobile (390px)** using headless Chromium.
   - Designed to demonstrate what a modernized conversion presence looks like for the client.
3. **One Personalized Quick Win Asset**:
   - Ready-to-use tactical asset (e.g., instant WhatsApp enquiry triage script or Google review response template) matching the diagnosed #1 bottleneck.
4. **Personalized WhatsApp Message**:
   - Human, short, non-spammy consultative outreach script for sales executives to copy with one click.
5. **Internal Sales Intelligence Brief**:
   - Internal-only target account discovery brief with SWOT highlights, consultative pitch angle, anticipated objection, and recommended counter.
6. **Complete Sales Pack ZIP Bundle**:
   - Downloadable archive containing `/report/`, `/website-preview/`, `/quick-win/`, `/sales/`, and `/metadata/audit.json`.

---

## 2. Architecture & Tech Stack

```
                                [ Sales Executive / UI ]
                                          │
                                 Paste 1 Business URL
                                          │
                                          ▼
                                ┌───────────────────┐
                                │   URL Classifier  │
                                └─────────┬─────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
          Google Maps Adapter      Website Adapter       Social Adapters
         (Playwright Chromium)    (BeautifulSoup / DOM)  (Instagram / FB)
                    └─────────────────────┬─────────────────────┘
                                          ▼
                                ┌───────────────────┐
                                │ Identity Resolver │
                                └─────────┬─────────┘
                                          ▼
                              ┌───────────────────────┐
                              │  Deterministic Scoring│ (100 pts, 6 dimensions)
                              └───────────┬───────────┘
                                          ▼
                              ┌───────────────────────┐
                              │   Opportunity Engine  │ (Isolates #1 Bottleneck)
                              └───────────┬───────────┘
                                          ▼
                ┌───────────────────────────────────────────────────┐
                │             Parallel Asset Generation             │
                │  • Playwright: Desktop (1440px) & Mobile (390px)  │
                │  • Playwright: 5-Page Strict A4 Consulting PDF    │
                │  • Quick Win Engine + WhatsApp Script Engine      │
                │  • Sales Brief Engine + ZIP Pack Assembler        │
                └─────────────────────────┬─────────────────────────┘
                                          ▼
                                [ Digital Growth Pack ]
```

- **Frontend**: Next.js 14 (App Router), TypeScript, Vanilla CSS design tokens, Lucide icons.
- **Backend**: FastAPI (Python 3.12), Pydantic v2 schemas, SQLite (`SQLAlchemy 2.0`), Jinja2 templates.
- **Visual & PDF Engine**: Playwright Chromium (strict deterministic rendering & page break verification).
- **AI Abstraction**: Provider architecture supporting `deterministic` rules, `ollama`, `gemini`, or `openai`.

---

## 3. Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- macOS / Linux / Windows WSL

### One-Command Startup
To start both backend and frontend together, execute:

```bash
./start.sh
```

- **Dashboard**: [http://localhost:3001](http://localhost:3001)
- **API Swagger Docs**: [http://127.0.0.1:8050/docs](http://127.0.0.1:8050/docs)

---

## 4. Manual Installation & Setup

### A. Backend Setup
```bash
# 1. Create and activate virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio

# 3. Install Playwright Chromium browser
playwright install chromium

# 4. Start FastAPI server on port 8050
PYTHONPATH=backend uvicorn app.main:app --host 127.0.0.1 --port 8050 --reload
```

### B. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- -p 3001
```

---

## 5. Configuration (`.env`)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8050` | Backend API port |
| `DATABASE_URL` | `sqlite:///./storage/onehive.db` | SQLite database URI |
| `AI_PROVIDER` | `deterministic` | Provider: `deterministic`, `ollama`, `gemini`, or `openai` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3` | Ollama model identifier |
| `GEMINI_API_KEY` | *(Optional)* | Google Gemini API key |
| `OPENAI_API_KEY` | *(Optional)* | OpenAI API key |
| `GOOGLE_MAPS_API_KEY` | *(Optional)* | Google Places API key (system uses layered scraping if empty) |
| `ONEHIVE_COMPANY_NAME` | `OneHive Technologies` | Centralized branding |
| `ONEHIVE_WEBSITE` | `www.onehivetech.com` | Centralized website |
| `ONEHIVE_PHONE` | `+91 98450 12345` | Contact number displayed on PDF Page 5 |
| `ONEHIVE_EMAIL` | `growth@onehivetech.com` | Contact email |

---

## 6. How It Works

### Deterministic 100-Point Scoring
The engine never allows an LLM to guess scores. Scoring is calculated deterministically across 6 core dimensions:
1. **Discoverability (20 pts)**: Google Business profile presence, title hygiene, address completeness, phone presence.
2. **Brand & Identity (15 pts)**: Name consistency, value proposition clarity, category positioning.
3. **Trust & Reputation (20 pts)**: Verified rating, review count, customer trust validation.
4. **Website Experience (15 pts)**: Mobile viewport responsiveness, navigation clarity, HTTPS security.
5. **Lead Conversion (20 pts)**: Instant WhatsApp CTA bridge, click-to-call, booking friction.
6. **Social Presence (10 pts)**: Instagram/Facebook connectivity and profile consistency.

### Strict 5-Page PDF Verification
Every generated PDF is run through an automated QA verifier (`PDFVerifier`) which checks:
- Exactly 5 pages (`page_count == 5`).
- Required section titles on each page.
- Zero forbidden phrases (`CONFIDENTIAL INTELLIGENCE`, `73%`, `lost customers`, `revenue lost`).
- Page 4 embeds an actual browser-frame screenshot of the personalized website preview.

---

## 7. Demo Mode vs. Real Mode

- **Real Mode**:
  - Paste any real Google Maps link, website, Instagram, or Facebook URL.
  - The engine gathers real evidence and resolves the actual business.
  - Target acceptance test: `https://maps.google.com/?cid=8429486214490638391...` strictly resolves to **Dr. Budhiraja** (Dentist in Mayur Vihar, New Delhi, 4.9★), **never** demo data.
- **Demo Mode**:
  - Click **"Load Demo Business"** on the dashboard.
  - Loads the pre-validated fixture for **Apex Dental & Implant Centre** without calling external scrapers.
  - Clearly tagged with a `DEMO DATA MODE` banner.

---

## 8. Running Automated Tests

Run the complete test suite:

```bash
# Run all specification requirements tests (URL classification, demo mode isolation, scoring, PDF 5-page rule, ZIP pack)
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/test_spec_requirements.py -v

# Run acceptance test against target Google Maps CID URL
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/test_target_cid_resolution.py -s -v
```

---

## 9. Extending The Engine

### Adding a New Research Adapter
1. Create a new adapter in `backend/app/research/your_adapter.py`.
2. Inherit from the base research interface and return `(BusinessIdentity, List[EvidenceItem], dict)`.
3. Register the adapter in `backend/app/services/identity_resolver.py`.

### Adding Industry Profiles
Industry heuristics are located in `backend/app/services/opportunity_engine.py`. To customize recommendations for a new vertical (e.g., real estate or fitness):
1. Define the vertical trigger keywords in `evaluate()`.
2. Add tailored journey mappings (`current_journey` vs. `improved_journey`).
3. Add the recommended OneHive service mapping.
