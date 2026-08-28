# 🎥 VidContext

**VidContext** is a full-stack AI-powered web application that helps users understand YouTube videos through **AI-generated summaries, automatic chapters, interactive transcripts, and conversational Q&A**.

The application uses a **Retrieval-Augmented Generation (RAG)** pipeline to retrieve relevant information from video transcripts and generate context-aware responses using **LangChain, FAISS, and Gemini**.

## 🚀 Features

* 🔍 **AI Video Summaries** — Generate concise summaries from YouTube video transcripts.

* 💬 **Chat with Videos** — Ask questions and have conversations about video content using RAG.

* 📄 **Interactive Transcripts** — View transcripts with synchronized scrolling and video seeking.

* 🧩 **Automatic Chapters** — Generate timestamped chapters to navigate videos easily.

* ✍️ **Rich-Text Notes** — Create and save notes for videos.

* 🔐 **Authentication** — Secure Google Sign-In using OAuth 2.0 and JWT.

* 🎨 **Modern UI** — Responsive interface built with Tailwind CSS, Shadcn UI, and GSAP.

## 🧠 How It Works

```text
YouTube Video
      ↓
Fetch Transcript
      ↓
Split Transcript into Chunks
      ↓
Generate Embeddings
      ↓
Store in FAISS
      ↓
User Query
      ↓
Semantic Search
      ↓
Relevant Context
      ↓
Gemini LLM
      ↓
AI Response
```

The RAG pipeline is implemented as a **Python Flask microservice**, while the main application uses a **MERN-based architecture**.

## 🛠️ Tech Stack

### Frontend

* React.js (Vite)
* TypeScript
* Tailwind CSS
* Shadcn UI
* GSAP
* React YouTube

### Backend

* Node.js
* Express.js
* MongoDB
* Mongoose
* JWT
* Google OAuth 2.0

### AI Service

* Python
* Flask
* LangChain
* FAISS
* Gemini API
* YouTranscript API

## 🏗️ Architecture

```text
             ┌──────────────────┐
             │   React Frontend │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ Node.js + Express│
             └───────┬──────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   ┌──────────────┐      ┌──────────────┐
   │   MongoDB    │      │ Flask AI API │
   └──────────────┘      └──────┬───────┘
                                │
                         ┌──────┴───────┐
                         ▼              ▼
                      FAISS          Gemini
```

## ⚙️ Getting Started

### Prerequisites

* Node.js 18+
* Python 3.9+
* MongoDB
* Google Cloud OAuth credentials
* Gemini API key

### Installation

Clone the repository:

```bash
git clone https://github.com/your-username/vidcontext.git
cd vidcontext
```

Install and run the backend:

```bash
cd backend

npm install

npm run dev
```

Run the AI service:

```bash
cd services

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python app.py
```

Run the frontend:

```bash
cd frontend

npm install

npm run dev
```

Configure the required environment variables in the `frontend`, `backend`, and `services` directories before running the application.

## 📌 Project Highlights

* Full-stack **MERN + Python microservice** architecture
* Retrieval-Augmented Generation (**RAG**)
* Vector similarity search using **FAISS**
* LLM integration using **Gemini**
* Google OAuth 2.0 + JWT authentication
* Interactive YouTube transcript and video integration
* Persistent user notes and video data
