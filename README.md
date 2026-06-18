# Mental-ai-chatbot
<div align="center">

# 🌸 Mirra AI — Your Compassionate Wellness Companion

[![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb)](https://mongodb.com)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-blue?style=for-the-badge&logo=google)](https://ai.google.dev)
[![Ollama](https://img.shields.io/badge/Ollama-Llama3.2-black?style=for-the-badge)](https://ollama.com)

*A real-world AI mental health companion with clinical NLP analysis, persistent memory, and secure authentication*

</div>

---

## ✨ What is Mirra AI?

Mirra AI is a full-stack AI-powered mental wellness chatbot that goes beyond simple conversation. It understands your emotions clinically, remembers your journey across sessions, and provides a safe, empathetic space — available 24/7.

Built as a production-grade application with real authentication, persistent memory, clinical analysis, and a beautiful glassmorphism UI.

---

## 🚀 Features

### 🤖 AI & Clinical Intelligence
- **Dual AI Architecture** — Google Gemini for empathetic responses + Ollama (Llama 3.2 3B) for local clinical NLP analysis
- **Clinical Taxonomy System** — detects emotion tags, intensity levels, trigger sources, and functional impact
- **Persistent Memory** — bot remembers past conversations and greets returning users personally
- **Loop Prevention** — anti-repetition system ensures varied, meaningful responses
- **Adaptive Intent Detection** — understands context across conversation history

### 🔐 Authentication & Security
- **Secure Google OAuth** — server-side JWT token verification with Google's API
- **Email/Password Auth** — with auth provider separation (prevents account mixing)
- **Multi-account Support** — switch between accounts with Google-style account switcher
- **Anonymous Mode** — toggle to chat without saving history

### 💬 Chat Experience
- **Conversation Sidebar** — real saved sessions grouped by date, clickable to reload
- **Session Management** — each conversation gets a unique session ID
- **Personalised Greeting** — "Welcome back! Last time you were feeling Overwhelmed..."
- **Typing Indicators** — animated dots while AI is thinking
- **Real-time Context** — last 10 messages passed as context to AI

### 👤 Profile & Settings
- **Avatar System** — upload photo from device or pick from emoji picker
- **Your Journey** — live stats: total conversations, top emotion, last chat date
- **Trusted Contact** — save an emergency contact with phone validation
- **Preferences** — toggleable daily reminders, mood tracking, anonymous mode
- **Delete Account** — wipes user + all chat history from MongoDB

### 🆘 Support Resources
- **Crisis Help** — verified Indian helplines (KIRAN, iCall, AASRA, Vandrevala)
- **Self-Care Guides** — practical wellness tips
- **Find a Therapist** — curated platforms (iCall TISS, YourDOST, Practo, MindPeers)
- **Community Resources** — peer support platforms
- **Daily Motivational Quotes** — rotates based on day of week

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JS (Glassmorphism UI) |
| **Backend** | FastAPI, Python 3.13 |
| **Database** | MongoDB Atlas (Motor async driver) |
| **AI — Responses** | Ollama (Llama 3.2 3B) — runs locally |
| **AI — Analysis** | Google Gemini via google-genai |
| **Auth** | Google OAuth 2.0 (server-side verification) |
| **NLP** | spaCy, custom clinical taxonomy system |
| **Security** | google-auth, certifi |

---

## 🏗️ Architecture

```
┌─────────────────┐     HTTP      ┌──────────────────┐
│   Frontend      │ ────────────► │   FastAPI        │
│   HTML/CSS/JS   │ ◄──────────── │   Backend        │
└─────────────────┘               └────────┬─────────┘
                                           │
                          ┌────────────────┼────────────────┐
                          │                │                 │
                   ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼──────┐
                   │  MongoDB    │  │   Ollama   │  │   Google   │
                   │  Atlas      │  │  Llama 3.2 │  │   Gemini   │
                   └─────────────┘  └────────────┘  └────────────┘
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Main chat with clinical analysis |
| `POST` | `/auth/signup` | Email/password registration |
| `POST` | `/auth/signin` | Email/password login |
| `POST` | `/auth/google` | Secure Google OAuth |
| `GET` | `/history/{user_id}` | Full message history |
| `GET` | `/sessions/{user_id}` | Grouped conversation sessions |
| `GET` | `/session/{session_id}` | Load specific session |
| `GET` | `/memory/{user_id}` | User memory summary for AI context |
| `DELETE` | `/auth/delete/{user_id}` | Delete account + all data |

---

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- MongoDB Atlas account (free tier works)
- Ollama installed
- Google Cloud OAuth credentials

### 1. Clone the repo
```bash
git clone https://github.com/AbWebDev29/Mental-AI-Chatbot-AG.git
cd Mental-AI-Chatbot-AG
```

### 2. Set up Python environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure environment variables
Create a `.env` file in the root:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
JWT_SECRET=your_jwt_secret_here
GOOGLE_API_KEY=your_gemini_api_key
```

### 4. Start Ollama
```bash
ollama serve
ollama pull llama3.2:3b
```

### 5. Start the backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 6. Start the frontend
```bash
cd frontend
python -m http.server 3000
```

### 7. Open in browser
```
http://localhost:3000
```

---

## 🔑 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → APIs & Services → Credentials → OAuth Client ID
3. Add authorized origins: `http://localhost:3000`
4. Add your Client ID to `frontend/signin.html`
5. Add yourself as a test user under Audience

---

## 📁 Project Structure

```
Mental-AI-Chatbot-AG/
├── backend/
│   ├── main.py                    # FastAPI app + all routes
│   ├── database.py                # MongoDB connection + save functions
│   ├── llm_service.py             # Ollama Llama integration
│   ├── nlp_engine.py              # Clinical NLP pipeline
│   └── clinical_analyzer_llama.py # Clinical taxonomy system
├── frontend/
│   ├── index.html                 # Landing page
│   ├── chat.html                  # Main chat interface
│   ├── signin.html                # Auth page
│   ├── profile.html               # Profile & settings
│   ├── support.html               # Support resources
│   ├── games.html                 # Wellness games
│   ├── about.html                 # About page
│   ├── auth.js                    # Shared auth & navbar logic
│   ├── styles/
│   │   └── global.css             # Global design system
│   └── assets/                    # Images & icons
└── .env                           # Environment variables (not committed)
```

---

## 👥 Team

Built by **Gayathri** & **Anvi** as part of a real-world AI engineering portfolio project.

| Feature | Owner |
|---------|-------|
| Auth, Profile, Settings | Gayathri Menon|
| Sidebar & Conversation Memory | Gayathri Menon|
| Google OAuth | Gayathri Menon|
| AI Response Engine | Shared |
| Frontend | Shared |
| Clinical NLP System | Anvi Bansal |
| Support Page | Anvi Bansal|
| Games Section | Anvi Bansal|

---

## 🚧 Roadmap

- [ ] RAG-powered memory (vector DB for long-term context)
- [ ] Voice input support
- [ ] Mood tracking dashboard with charts
- [ ] Push notifications for daily check-ins
- [ ] Mobile app (React Native)
- [ ] Therapist referral integration

---

## ⚠️ Disclaimer

Mirra AI is an AI companion and is **not a replacement** for professional mental health care. If you or someone you know is in crisis, please contact a mental health professional or call **KIRAN: 1800-599-0019** (India, free, 24/7).

---

<div align="center">
Made with 💜 · Your thoughts are safe here · Mirra AI 2026
</div>
