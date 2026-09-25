# AIVOA.AI — AI-Powered Deviation Intake

A working pharmaceutical QMS deviation-intake module. It accepts a PDF, DOCX, TXT, or pasted report/email; sends extracted text through a controlled LangGraph + Groq workflow; presents editable AI suggestions; and saves only after human review to PostgreSQL.

This is a **Deviation Management** module, not a customer-complaints workflow. AI impact and severity are explicitly initial recommendations, not official QA classifications.

## Architecture

```text
React + Redux Toolkit (frontend)  →  FastAPI API  →  LangGraph / Groq
                                           ↓
                                      PostgreSQL
```

`backend/app/api` contains HTTP routes; `services` owns persistence operations; `utils/document_parser.py` extracts files; `graph/deviation_graph.py` contains the typed LangGraph pipeline; Pydantic schemas constrain API and model output; SQLAlchemy owns the `deviations` table.

## Project structure

```text
frontend/                 React/Vite application
  src/components/         Enterprise UI components
  src/features/           Redux deviation slice
  src/pages/              Intake, list, detail and edit routes
  src/services/           API client
backend/
  app/api/                FastAPI routes
  app/ai/                 Dedicated prompts
  app/graph/              Typed LangGraph workflow
  app/models/             SQLAlchemy models
  app/schemas/            Pydantic contracts
  app/services/           Persistence business logic
  app/utils/              PDF/DOCX/TXT extraction
  tests/                  API tests
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- A Groq API key

## Configure PostgreSQL and environment

Create a database, for example:

```sql
CREATE DATABASE aivoa_deviations;
```

Copy `backend/.env.example` to `backend/.env` and set the values:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/aivoa_deviations
CORS_ORIGINS=http://localhost:5173
MAX_UPLOAD_MB=10
```

Tables are created on API startup for this challenge. In a production system, replace this startup creation with Alembic migrations.

## Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Check `http://localhost:8000/api/health` and browse the OpenAPI docs at `http://localhost:8000/docs`.

## Start the frontend

In another terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open the URL printed by Vite (normally `http://localhost:5173`). `VITE_API_BASE_URL` defaults to `http://localhost:8000/api` if omitted.

## LangGraph workflow

The application invokes a real, sequential LangGraph workflow:

```text
START → ingest_input → extract_text → extract_deviation → validate_extraction
      → impact_analysis → severity_analysis → generate_explanation → finalize_result → END
```

The extraction and validation nodes use the strict `ExtractionOutput` Pydantic model; no free-form result is used to populate the UI. The assessment nodes use a separate `RecommendationOutput` contract. Prompts specifically prohibit fabrication, keep absent data null, and label recommendations as requiring human QA review. A missing Groq key or failed model request returns a clean API error rather than saving anything.

## Redux flow

`deviationSlice` owns `formData`, analysis result, processing/saving state, source markers, missing information, confidence, upload reference, errors, and assistant messages. On a successful `/analyze` result, `setAnalysisResult` transfers non-empty structured extraction fields into `formData` and marks them **AI Suggested**. Any form edit dispatches `setField`, which changes that field to **Edited**. Saving posts the reviewed Redux form to the API; analysis never persists automatically.

## Database schema

The PostgreSQL `deviations` table stores core intake fields, reviewed impact/severity, AI suggested impact/severity/reason/confidence, the raw structured extraction as JSONB, status (`Draft`, `Submitted`, `Under Review`, `Closed`), and timestamps. The demo flow saves records as `Draft`.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | API health check |
| POST | `/api/deviations/analyze` | Multipart `text` and/or `file`; runs document extraction and LangGraph |
| POST | `/api/deviations` | Save a reviewed record |
| GET | `/api/deviations` | List records, optional `?q=` search |
| GET | `/api/deviations/{id}` | Get detail |
| PUT | `/api/deviations/{id}` | Update a record |
| DELETE | `/api/deviations/{id}` | Delete a record |
| POST | `/api/deviations/chat` | Ask a context-constrained assistant question |

## Demo workflow

1. Open **Log Deviation** at `/deviations/new`.
2. Use **Load sample scenario**, paste an email, or upload a PDF/DOCX/TXT.
3. Click **Analyze Deviation**. The live request invokes the backend workflow.
4. Verify the generated fields and recommendation panel; absent material facts are listed.
5. Change an AI-populated field and observe its **Edited** marker.
6. Complete required fields (site, occurrence date, title, detailed description) and save.
7. The detail page confirms the draft; navigate to **Deviations** to see history.

The supplied sample is source content only, never a hardcoded AI response:

> During manufacturing of API Intermediate X, reactor temperature reached 82°C for approximately 18 minutes; the approved range was 75°C to 80°C. It was found during routine monitoring and returned within range. Site: API Manufacturing Unit. Date: 2026-09-24. Source: Production. Batch: API-260924-B17.

## Tests

```powershell
cd backend
pytest
```

The API tests cover health, invalid analysis input, mocked-but-schema-validated structured analysis response, and save/get persistence with SQLite test configuration. Manual UI checks cover uploads, paste analysis, auto-population, editing, and saves.

## Known limitations and next improvements

- Groq availability and structured-output support depend on the configured model/account; the configured `llama-3.3-70b-versatile` is the intended model.
- Image-only/scanned PDFs need OCR, which is deliberately not included.
- Startup `create_all` is practical for the challenge but Alembic migrations should be added for production.
- Add SSO/RBAC, immutable audit events, virus scanning, malware-safe object storage, retention policies, richer search, and async task progress for production scale.
