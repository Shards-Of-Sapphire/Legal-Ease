# 🧠 LegalEase — Simplifying Legal Jargon with AI

**LegalEase** is a smart legal document summarization web app built by **Sapphire**, a visionary team committed to creating tools that empower and outgrow the ordinary.

This AI-powered app accepts PDF, DOCX, or TXT legal documents and summarizes them into readable, layman-friendly language using transformer-based models like Longformer.

---

## 🚀 Features

- 📄 Upload legal documents (PDF, DOCX, or TXT)
- 🧠 AI summarization using Longformer (4096+ tokens)
- 🧾 Extract and simplify dense legal content
- 🔍 Frontend built with clean HTML/CSS/JS
- 💡 Backend powered by Flask + Hugging Face

---

## 💻 Tech Stack

| Layer        | Tech                              |
|-------------|-----------------------------------|
| Frontend     | HTML, CSS, JavaScript             |
| Backend      | Python (Flask)                    |
| AI Engine    | `allenai/longformer-base-4096`    |
| File Parsing | PyMuPDF (PDF), python-docx (DOCX) |
| Deployment   | Replit / Render / Localhost       |

---

## 🛠 Setup & Run Locally

```bash
# Clone the repository
git clone https://github.com/sapphire-team/legalease.git
cd legalease

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app locally
python main.py
