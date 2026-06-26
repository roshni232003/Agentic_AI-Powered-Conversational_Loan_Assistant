 🏦 SVU Finance — Agentic AI Loan Assistant
### Final Year Project | Swami Vivekananda University

---

## ⚡ FASTEST WAY TO RUN (Docker — 3 commands)

```bash
# 1. Copy env file and add your OpenAI key
cp .env.example .env
# Open .env and paste your OpenAI API key

# 2. Build and start everything
docker-compose up --build

# 3. Open in browser
# Chat UI  → http://localhost:8501
# API Docs → http://localhost:8000/docs
```

---

## 🐢 MANUAL WAY (Step by Step)

### STEP 1 — Install Python 3.11
Download from: https://python.org/downloads
✅ Check "Add to PATH" during install

### STEP 2 — Install PostgreSQL
Download from: https://postgresql.org/download
- Username: postgres
- Password: password (remember this!)
- Port: 5432

### STEP 3 — Install Tesseract OCR
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Mac: `brew install tesseract`
- Linux: `sudo apt install tesseract-ocr`

### STEP 4 — Clone / Download this project
Put it in a folder, open terminal there.

### STEP 5 — Create virtual environment
```bash
python -m venv venv

# Activate it:
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### STEP 6 — Install all packages
```bash
pip install -r requirements.txt
```

### STEP 7 — Set up environment variables
```bash
cp .env.example .env
```
Open `.env` and fill in:
- `OPENAI_API_KEY` = your key from platform.openai.com
- `DATABASE_URL` = postgresql://postgres:YOUR_PASSWORD@localhost:5432/loan_db

### STEP 8 — Create the database
Open pgAdmin or psql and run:
```sql
CREATE DATABASE loan_db;
```
Then run:
```bash
python database.py
```

### STEP 9 — Train the ML model (run ONCE)
```bash
python ml/train_model.py
```
You should see: "Model saved to ml/credit_model.pkl"

### STEP 10 — Start the API server
```bash
uvicorn main:app --reload
```
✅ API running at: http://localhost:8000
✅ API Docs at:    http://localhost:8000/docs

### STEP 11 — Start the chat frontend (new terminal)
```bash
# Activate venv again in new terminal
venv\Scripts\activate

streamlit run frontend/streamlit_app.py
```
✅ Chat UI at: http://localhost:8501

---

## 📁 Project Structure

```
loan-assistant/
├── main.py                      ← FastAPI server (all endpoints)
├── database.py                  ← PostgreSQL models & connection
├── requirements.txt             ← All Python packages
├── Dockerfile                   ← Docker container config
├── docker-compose.yml           ← Run everything together
├── .env.example                 ← Copy to .env and fill keys
│
├── agents/
│   ├── master_agent.py          ← BOSS: orchestrates all agents
│   ├── sales_agent.py           ← Greets & convinces customer
│   ├── worker_agent.py          ← Collects customer data
│   ├── verification_agent.py    ← KYC document verification
│   ├── credit_agent.py          ← ML credit scoring (XGBoost)
│   ├── approval_agent.py        ← Approve / Reject decision
│   └── letter_agent.py          ← Generate PDF sanction letter
│
├── ml/
│   ├── train_model.py           ← Train XGBoost model (run once)
│   ├── credit_model.pkl         ← Saved model (auto-generated)
│   └── feature_names.pkl        ← Feature list (auto-generated)
│
├── utils/
│   ├── pdf_generator.py         ← Professional PDF generation
│   └── ocr_utils.py             ← Tesseract OCR for documents
│
├── frontend/
│   └── streamlit_app.py         ← Chat UI (Streamlit)
│
└── sanction_letters/            ← Generated PDFs saved here
```

---

## 🔌 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET    | /   | Health check |
| POST   | /session/new | Create new session |
| POST   | /chat | Send message, get reply |
| GET    | /chat/history/{id} | Get conversation history |
| POST   | /upload/document/{id} | Upload KYC image for OCR |
| GET    | /download/sanction/{id} | Download sanction letter PDF |
| GET    | /session/{id}/status | Get full session status |

---

## 🤖 How the 7 Agents Work

```
User Message
    ↓
Master Agent (Orchestrator)
    ↓ routes to...
    ├── Sales Agent       → Greeting & product explanation
    ├── Worker Agent      → Collects 13 data fields
    ├── Verification Agent → KYC check (PAN + Aadhaar)
    ├── Credit Risk Agent  → XGBoost ML credit scoring
    ├── Approval Agent     → Approve / Reject / Need Docs
    └── Letter Agent       → Generate PDF sanction letter
```

---

## 🚀 Deploy to Cloud (Render.com — FREE)

1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Set environment variables (OPENAI_API_KEY, DATABASE_URL)
5. Build command: `pip install -r requirements.txt && python ml/train_model.py`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Done! Live URL in 5 minutes 🎉

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| AI/LLM | OpenAI GPT-4o-mini |
| Agent Framework | LangChain |
| Backend API | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| ML Model | XGBoost |
| OCR | Tesseract |
| PDF Generation | FPDF2 |
| Frontend | Streamlit |
| Containerization | Docker |

---

Made with ❤️ for SVU Final Year Project
