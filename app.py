import streamlit as st
from groq import Groq
from fpdf import FPDF
import psycopg2
import random, string, re, json
from datetime import datetime, timedelta

st.set_page_config(page_title="SVU Finance – ARIA", page_icon="🏦", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.header { background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); color: white; padding: 20px 28px; border-radius: 16px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 20px rgba(13,71,161,0.3); }
.header h1 { margin:0; font-size:1.6rem; font-weight:700; }
.header p  { margin:4px 0 0; opacity:0.85; font-size:1rem; font-weight:700; }
.stage-bar { display:flex; gap:6px; overflow-x:auto; padding:8px 0; margin-bottom:10px; scrollbar-width:none; }
.stage-bar::-webkit-scrollbar { display:none; }
.pill { padding:4px 12px; border-radius:20px; font-size:11px; font-weight:600; white-space:nowrap; border:1.5px solid #e0e0e0; color:#9e9e9e; background:white; }
.pill.active { background:#0d47a1; color:white; border-color:#0d47a1; }
.pill.done   { background:#e8f5e9; color:#2e7d32; border-color:#a5d6a7; }
.sidebar-header { background:#0d47a1; color:white; padding:16px; border-radius:12px; text-align:center; margin-bottom:16px; }
.sidebar-header h3 { margin:0; font-size:1rem; color:white; }
.sidebar-header p  { margin:4px 0 0; font-size:0.8rem; opacity:0.8; color:white; }
</style>
""", unsafe_allow_html=True)

# ── Groq Client ───────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# ── Database (Neon Cloud) ─────────────────────────────────────
def get_db():
    return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode="require")


def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id           SERIAL PRIMARY KEY,
                name         VARCHAR(100),
                phone        VARCHAR(20),
                income       NUMERIC,
                credit_score INTEGER,
                loan_amount  NUMERIC,
                status       VARCHAR(50) DEFAULT 'pending',
                created_at   TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.warning(f"DB init: {e}")


def save_customer(data: dict):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO customers (name, phone, income, credit_score, loan_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            str(data.get("name", "Unknown")),
            str(data.get("phone", "N/A")),
            float(data.get("income", 0) or 0),
            int(data.get("credit_score", 0) or 0),
            float(data.get("loan_amount", 0) or 0),
            str(data.get("status", "pending")),
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.warning(f"Save error: {e}")


def get_stats():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM customers;")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM customers WHERE status='approved';")
        approved = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM customers WHERE status='rejected';")
        rejected = cur.fetchone()[0]
        cur.close()
        conn.close()
        return total, approved, rejected
    except Exception:
        return None, None, None


def get_previous_applications():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, phone, income, credit_score, loan_amount, status
            FROM customers
            WHERE name IS NOT NULL
            AND LENGTH(TRIM(name)) > 2
            AND name NOT IN ('N/A','Unknown','None','null')
            ORDER BY id DESC LIMIT 10
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception:
        return []


# ── EMI (Reducing Balance) ────────────────────────────────────
def calculate_emi(loan_amount: float, tenure: int, annual_rate: float = 0.115) -> float:
    r = annual_rate / 12
    emi = loan_amount * r * (1 + r) ** tenure / ((1 + r) ** tenure - 1)
    return round(emi, 2)


# ── Approval PDF ──────────────────────────────────────────────
def generate_approval_pdf(data: dict) -> bytes:
    loan_amount = float(data.get("loan_amount", 0))
    tenure = int(data.get("tenure", 12))
    credit_score = int(data.get("credit_score", 700))
    rate = 0.115 if credit_score >= 750 else 0.135
    emi = calculate_emi(loan_amount, tenure, rate)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(13, 71, 161)
    pdf.rect(0, 0, 210, 32, "F")
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "SVU FINANCE - LOAN SANCTION LETTER", align="C")
    pdf.ln(30)
    ref = "SVU/LOAN/" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    today = datetime.today()
    expiry = today + timedelta(days=30)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Ref: {ref}    |    Date: {today.strftime('%d %B %Y')}", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(13, 71, 161)
    pdf.cell(0, 8, f"To: {str(data.get('name', '')).upper()}", ln=True)
    pdf.ln(3)
    pdf.set_fill_color(227, 242, 253)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 10, f"  Subject: Loan Sanction of Rs {loan_amount:,.0f}", ln=True, fill=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 7,
                   f"Dear {data.get('name', '')},\n\nWe are pleased to inform you that your loan application has been APPROVED by SVU Finance.")
    pdf.ln(4)
    rows = [
        ("Sanctioned Amount", f"Rs {loan_amount:,.2f}"),
        ("Loan Tenure", f"{tenure} Months"),
        ("Interest Rate", f"{rate * 100:.1f}% p.a."),
        ("Monthly EMI", f"Rs {emi:,.2f}"),
        ("Loan Purpose", str(data.get("purpose", ""))),
        ("Credit Score", str(credit_score)),
        ("Processing Fee", f"Rs {loan_amount * 0.01:,.2f}"),
        ("Valid Until", expiry.strftime("%d %B %Y")),
    ]
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(13, 71, 161)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(95, 9, "  DETAIL", border=0, fill=True)
    pdf.cell(95, 9, "  VALUE", border=0, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 10)
    for i, (k, v) in enumerate(rows):
        fill = i % 2 == 0
        pdf.set_fill_color(232, 240, 253) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(95, 9, f"  {k}", border=1, fill=fill)
        pdf.cell(95, 9, f"  {v}", border=1, fill=fill, ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(13, 71, 161)
    pdf.cell(0, 7, "Terms & Conditions:", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    for t in ["1. Sanction valid for 30 days.", "2. Disbursement subject to document verification.",
              "3. Prepayment after 6 EMIs with 2% charge.", "4. EMI via NACH auto-debit."]:
        pdf.cell(0, 6, t, ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(13, 71, 161)
    pdf.cell(0, 7, "Authorised By:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, "Ms. Sangita Bose - Head, Credit Operations, SVU Finance", ln=True)
    pdf.ln(6)
    pdf.set_fill_color(232, 245, 233)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(27, 94, 32)
    pdf.cell(0, 12, "Congratulations! Your loan has been sanctioned.", align="C", fill=True, ln=True)
    return bytes(pdf.output())


# ── Rejection PDF ─────────────────────────────────────────────
def generate_rejection_pdf(data: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(183, 28, 28)
    pdf.rect(0, 0, 210, 32, "F")
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "SVU FINANCE - LOAN REJECTION LETTER", align="C")
    pdf.ln(30)
    ref = "SVU/REJ/" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    today = datetime.today()
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Ref: {ref}    |    Date: {today.strftime('%d %B %Y')}", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(0, 8, f"To: {str(data.get('name', 'Applicant')).upper()}", ln=True)
    pdf.ln(3)
    pdf.set_fill_color(255, 235, 238)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(0, 10, "  Subject: Loan Application — Not Approved", ln=True, fill=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 7,
                   f"Dear {data.get('name', 'Applicant')},\n\nThank you for applying. After careful review, we are unable to approve your loan at this time.")
    pdf.ln(4)
    rows = [
        ("Applicant Name", str(data.get("name", "N/A"))),
        ("Mobile Number", str(data.get("phone", "N/A"))),
        ("Loan Requested", f"Rs {float(data.get('loan_amount', 0)):,.0f}"),
        ("Monthly Income", f"Rs {float(data.get('income', 0)):,.0f}"),
        ("Credit Score", str(data.get("credit_score", "N/A"))),
        ("Decision Date", today.strftime("%d %B %Y")),
    ]
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(183, 28, 28)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(95, 9, "  DETAIL", border=0, fill=True)
    pdf.cell(95, 9, "  VALUE", border=0, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 10)
    for i, (k, v) in enumerate(rows):
        fill = i % 2 == 0
        pdf.set_fill_color(255, 235, 238) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(95, 9, f"  {k}", border=1, fill=fill)
        pdf.cell(95, 9, f"  {v}", border=1, fill=fill, ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(0, 8, "Reasons for Rejection:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    for r in data.get("reasons", ["Credit score below threshold", "Insufficient income"]):
        pdf.cell(0, 7, f"  * {r}", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(27, 94, 32)
    pdf.cell(0, 8, "How to Improve:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    for t in ["Pay all EMIs on time to improve credit score",
              "Reduce existing loans before reapplying",
              "Add a co-applicant with higher income",
              "Reapply after 90 days"]:
        pdf.cell(0, 7, f"  * {t}", ln=True)
    pdf.ln(6)
    pdf.set_fill_color(255, 235, 238)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(0, 12, "We hope to serve you better in the future.", align="C", fill=True, ln=True)
    return bytes(pdf.output())


def regenerate_pdf(name, loan_amount, credit_score, tenure=60) -> bytes:
    return generate_approval_pdf({
        "name": name, "loan_amount": loan_amount,
        "credit_score": credit_score, "tenure": tenure,
        "purpose": "Personal Use"
    })


# ── System Prompt ─────────────────────────────────────────────
SYSTEM = """You are ARIA (Agentic Risk-based Intelligent Assistant), a friendly AI Loan Assistant for SVU Finance. Warm, professional, conversational.

STRICT FLOW:

PHASE 1 - GREETING: Introduce as ARIA. Ask loan type: Personal/Home/Education/Business. Explain briefly. Ask to proceed.

PHASE 2 - DATA COLLECTION (ONE at a time):
1.Full Name 2.Mobile 3.Email 4.PAN (ABCDE1234F) 5.Aadhaar (12 digits) 6.Age 7.Employment (Salaried/Self-Employed) 8.Years Employed 9.Monthly Income (Rs) 10.Existing Loans 11.Loan Amount (Rs) 12.Tenure (12/24/36/48/60 months) 13.Purpose
Show summary after all 13. Confirm.

PHASE 3 - KYC: Validate PAN & Aadhaar. Say KYC VERIFIED or ask re-enter.

PHASE 4 - CREDIT CHECK:
Score = 750 base, -150 if income<20000, -30 per loan, +5 per year employed, clamp 300-900.
DO NOT calculate EMI yourself. Just show Credit Score and Risk Grade.
The system will calculate EMI automatically.

PHASE 5 - DECISION:
APPROVE if: score>=650, income>=20000, loans<=3, age 21-65, EMI<=50% income.
REJECT with reasons. Output EXACTLY:
REJECTION_DATA
{"name":"...","phone":"...","loan_amount":...,"income":...,"credit_score":...,"reasons":["...","..."]}

PHASE 6 - SANCTION (approved only). Output EXACTLY:
GENERATE_PDF
{"name":"...","loan_amount":...,"tenure":...,"income":...,"credit_score":...,"purpose":"...","phone":"..."}

RULES: 3-5 lines max. One question at a time. Use Rs. Answer finance questions professionally."""


def process_reply(reply: str):
    if "GENERATE_PDF" in reply:
        parts = reply.split("GENERATE_PDF")
        text_part = parts[0].strip()
        json_part = parts[1].strip() if len(parts) > 1 else "{}"
        try:
            match = re.search(r'\{.*\}', json_part, re.DOTALL)
            if match:
                pdf_data = json.loads(match.group())
                pdf_bytes = generate_approval_pdf(pdf_data)
                name = pdf_data.get("name", "Customer").replace(" ", "_")
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.pdf_name = f"Sanction_{name}.pdf"
                st.session_state.pdf_type = "approved"
                save_customer({
                    "name": pdf_data.get("name", "Unknown"),
                    "phone": pdf_data.get("phone", "N/A"),
                    "income": pdf_data.get("income", 0),
                    "credit_score": pdf_data.get("credit_score", 0),
                    "loan_amount": pdf_data.get("loan_amount", 0),
                    "status": "approved",
                })
                return text_part + "\n\n📄 Sanction letter ready! Download from sidebar ⬅️\n✅ Saved to cloud database!"
        except Exception:
            pass
        return text_part

    if "REJECTION_DATA" in reply and not st.session_state.get("rejection_saved"):
        st.session_state.rejection_saved = True
        parts = reply.split("REJECTION_DATA")
        text_part = parts[0].strip()
        json_part = parts[1].strip() if len(parts) > 1 else "{}"
        try:
            match = re.search(r'\{.*\}', json_part, re.DOTALL)
            if match:
                rej_data = json.loads(match.group())
                pdf_bytes = generate_rejection_pdf(rej_data)
                name = rej_data.get("name", "Applicant").replace(" ", "_")
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.pdf_name = f"Rejection_{name}.pdf"
                st.session_state.pdf_type = "rejected"
                save_customer({
                    "name": rej_data.get("name", "Unknown"),
                    "phone": rej_data.get("phone", "N/A"),
                    "income": rej_data.get("income", 0),
                    "credit_score": rej_data.get("credit_score", 0),
                    "loan_amount": rej_data.get("loan_amount", 0),
                    "status": "rejected",
                })
                return text_part + "\n\n📄 Rejection letter ready! Download from sidebar ⬅️\n💾 Saved to cloud database."
        except Exception:
            pass
        return text_part

    return reply


def get_stage(messages):
    text = " ".join([m["content"] for m in messages[-6:]]).lower()
    if "sanction" in text or "rejection letter" in text: return 6
    if "approved" in text or "rejected" in text: return 5
    if "credit score" in text or "risk grade" in text: return 4
    if "kyc verified" in text: return 3
    if "full name" in text or "pan" in text or "income" in text: return 2
    if "personal loan" in text or "home loan" in text or "proceed" in text: return 1
    return 0


def get_ai_reply(history):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": SYSTEM}] + history,
        temperature=0.4, max_tokens=500,
    )
    return response.choices[0].message.content


# ── Session State ─────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = []
if "pdf_bytes" not in st.session_state: st.session_state.pdf_bytes = None
if "pdf_name" not in st.session_state: st.session_state.pdf_name = "letter.pdf"
if "pdf_type" not in st.session_state: st.session_state.pdf_type = None
if "started" not in st.session_state: st.session_state.started = False
if "rejection_saved" not in st.session_state: st.session_state.rejection_saved = False

init_db()
current_stage = get_stage(st.session_state.messages)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h3>🏦 SVU Finance</h3><p>AI Loan Assistant · ARIA</p></div>',
                unsafe_allow_html=True)
    stage_names = ["👋 Welcome", "📋 Product", "📝 Details", "🔍 KYC", "📊 Credit", "⚖️ Decision", "📄 Letter"]
    st.markdown("**Application Progress:**")
    st.progress((current_stage + 1) / len(stage_names))
    st.caption(f"Stage: {stage_names[current_stage]}")
    st.divider()

    if st.session_state.pdf_bytes:
        if st.session_state.pdf_type == "approved":
            st.success("✅ Loan Approved!")
        else:
            st.error("❌ Application Rejected")
        st.download_button("⬇️ Download Letter", data=st.session_state.pdf_bytes,
                           file_name=st.session_state.pdf_name, mime="application/pdf", use_container_width=True)
        st.divider()

    if st.button("🔄 New Application", use_container_width=True):
        for k in ["messages", "history", "pdf_bytes", "started", "rejection_saved", "pdf_name", "pdf_type"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    st.divider()
    st.markdown("**📊 Live Stats:**")
    total, approved, rejected = get_stats()
    if total is not None:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total)
        col2.metric("✅", approved)
        col3.metric("❌", rejected)
    else:
        st.warning("⚠️ DB not connected")

    st.divider()
    st.markdown("**📂 Previous Applications:**")
    apps = get_previous_applications()
    if apps:
        for row in apps:
            app_id = row[0]
            name = str(row[1] or "")
            phone = str(row[2] or "N/A")
            income = float(row[3] or 0)
            credit_score = int(row[4] or 0)
            loan_amount = float(row[5] or 0)
            status = str(row[6] or "")
            with st.expander(f"{'✅' if status == 'approved' else '❌'} {name}"):
                st.write(f"📞 **Phone:** {phone}")
                st.write(f"💰 **Loan:** Rs {loan_amount:,.0f}")
                st.write(f"🏅 **Score:** {credit_score}")
                st.write(f"📊 **Income:** Rs {income:,.0f}")
                if status == "approved":
                    pdf_b = regenerate_pdf(name, loan_amount, credit_score)
                    st.download_button("⬇️ Sanction Letter", data=pdf_b,
                                       file_name=f"Sanction_{name}.pdf", mime="application/pdf",
                                       key=f"dl_{app_id}", use_container_width=True)
                else:
                    pdf_b = generate_rejection_pdf({"name": name, "phone": phone,
                                                    "loan_amount": loan_amount, "income": income,
                                                    "credit_score": credit_score})
                    st.download_button("⬇️ Rejection Letter", data=pdf_b,
                                       file_name=f"Rejection_{name}.pdf", mime="application/pdf",
                                       key=f"dl_{app_id}", use_container_width=True)
    else:
        st.info("No applications yet.")

# ── Header ────────────────────────────────────────────────────
st.markdown('<div class="header"><h1>🏦 SVU Finance — ARIA</h1><p><b>AI-Powered Loan Assistant</b></p></div>',
            unsafe_allow_html=True)
stages = ["👋 Welcome", "📋 Product", "📝 Details", "🔍 KYC", "📊 Credit", "⚖️ Decision", "📄 Letter"]
pills = "".join(
    [f'<div class="pill {"done" if i < current_stage else "active" if i == current_stage else "pill"}">{s}</div>' for
     i, s in enumerate(stages)])
st.markdown(f'<div class="stage-bar">{pills}</div>', unsafe_allow_html=True)

# ── Auto greeting ─────────────────────────────────────────────
if not st.session_state.started:
    with st.spinner("ARIA is starting up..."):
        st.session_state.history.append({"role": "user", "content": "hello"})
        reply = get_ai_reply(st.session_state.history)
        reply = process_reply(reply)
        st.session_state.history.append({"role": "assistant", "content": reply})
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.started = True

# ── Render messages ───────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🏦" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────
if prompt := st.chat_input("Type your reply here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🏦"):
        with st.spinner("ARIA is thinking..."):
            reply = get_ai_reply(st.session_state.history)
            reply = process_reply(reply)
        st.session_state.history.append({"role": "assistant", "content": reply})
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.markdown(reply)
        st.rerun()
