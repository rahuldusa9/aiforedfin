# AI FOR EDUCATION – Adaptive Intelligent Learning System

A comprehensive AI-powered educational platform that combines adaptive learning, machine learning predictions, and generative AI to create a personalized student experience.

![Theme: Black & White Minimal](https://img.shields.io/badge/Theme-Black%20%26%20White-000000?style=flat-square&labelColor=000000&color=FFFFFF)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)
![React](https://img.shields.io/badge/Frontend-React%20+%20Vite-61DAFB?style=flat-square)
![ML](https://img.shields.io/badge/ML-Scikit--learn-F7931E?style=flat-square)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [ML Models](#ml-models)
- [UI Screenshots (Mock Layout)](#ui-screenshots-mock-layout)

---

## Features

### 1. AI Podcast
- Enter any topic → generates a 2-speaker podcast script via Gemini AI
- Converts script to multi-speaker MP3 using Edge TTS
- Refines audio with PyDub (normalization, fades)
- Waveform-style minimal audio player

### 2. AI Quiz
- Select topic, difficulty, and number of questions
- AI-generated multiple choice questions
- Submit answers → get score + ML performance prediction
- Predicts: performance level, recommended difficulty, weakness probability

### 3. AI Storytelling
- Converts topics into narrative educational stories
- Generates audio narration
- Animated reading cursor for text follow-along

### 4. AI Tutor
- Generates structured learning paths (4-5 steps)
- Each step includes: concept explanation, examples, mini test
- Progress tracking with step completion

### 5. AI Friend
- Chat interface with sentiment analysis (Naive Bayes ML)
- Detects: positive, neutral, stressed, anxious
- Switches to supportive tone when negative sentiment detected
- Logs emotional state to database

---

## Tech Stack

| Layer        | Technology                          |
|-------------|-------------------------------------|
| Frontend    | React.js (Vite), Tailwind CSS       |
| Backend     | Python (FastAPI), REST API           |
| Database    | mongodb            |
| AI/LLM      | Google Gemini API                   |
| TTS         | Edge TTS, PyDub                     |
| ML          | Scikit-learn (RandomForest, LogisticRegression, Naive Bayes) |

---

## Project Structure

```
ai-for-education/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy engine & session
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   ├── models/              # Database models
│   │   ├── user.py          #   users table
│   │   ├── quiz.py          #   quiz_results table
│   │   ├── learning.py      #   learning_progress table
│   │   └── emotional.py     #   emotional_logs table
│   ├── services/            # Business logic
│   │   ├── gemini_service.py    # Gemini AI integration
│   │   ├── tts_service.py       # Edge TTS + PyDub
│   │   ├── podcast_service.py   # Podcast orchestration
│   │   ├── quiz_service.py      # Quiz + ML prediction
│   │   ├── story_service.py     # Story generation
│   │   ├── tutor_service.py     # Learning path generation
│   │   └── friend_service.py    # Chat + sentiment
│   ├── ml/                  # Machine learning
│   │   ├── generate_dataset.py  # Synthetic dataset (2500 rows)
│   │   ├── train_model.py       # Performance model training
│   │   ├── sentiment_model.py   # Sentiment classifier
│   │   └── predictor.py         # Prediction interface
│   ├── routes/              # API route handlers
│   │   ├── auth.py          # Authentication
│   │   ├── podcast.py       # Podcast endpoints
│   │   ├── quiz.py          # Quiz endpoints
│   │   ├── story.py         # Story endpoints
│   │   ├── tutor.py         # Tutor endpoints
│   │   ├── friend.py        # Friend endpoints
│   │   ├── ml_routes.py     # ML prediction endpoints
│   │   └── dashboard.py     # Dashboard stats
│   └── audio_output/        # Generated audio files
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx         # Entry point
│       ├── App.jsx          # Router
│       ├── api.js           # API client (Axios)
│       ├── index.css        # Global styles
│       ├── components/
│       │   ├── Layout.jsx   # Sidebar + layout
│       │   └── UI.jsx       # Reusable components
│       └── pages/
│           ├── Dashboard.jsx
│           ├── Podcast.jsx
│           ├── Quiz.jsx
│           ├── Story.jsx
│           ├── Tutor.jsx
│           └── Friend.jsx
├── database/                # SQLite database directory
└── README.md
```

---

## Setup Instructions

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **npm** or **yarn**
- **FFmpeg** (required for PyDub audio processing)
  - Windows: Download from https://ffmpeg.org/download.html and add to PATH
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env and set your GEMINI_API_KEY
```

**Get Gemini API Key:**
1. Go to https://aistudio.google.com/apikey
2. Create an API key
3. Paste it in `backend/.env` as `GEMINI_API_KEY=your_key_here`

```bash
# Start the backend server
python main.py
# OR
uvicorn main:app --reload --port 8000
```

The server will:
- Initialize the SQLite database
- Auto-train ML models on first startup
- Serve API at http://localhost:8000
- Swagger docs at http://localhost:8000/docs

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at http://localhost:5173

### 3. Verify

1. Open http://localhost:5173 in your browser
2. You should see the black & white Dashboard
3. Navigate using the left sidebar
4. Try generating a quiz or chatting with AI Friend

---

## API Documentation

FastAPI auto-generates interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint                    | Description                    |
|--------|----------------------------|--------------------------------|
| POST   | `/api/auth/register`        | Register new user              |
| POST   | `/api/auth/login`           | Login                          |
| POST   | `/api/podcast/generate`     | Generate AI podcast            |
| POST   | `/api/quiz/generate`        | Generate quiz questions         |
| POST   | `/api/quiz/submit`          | Submit quiz & get ML prediction|
| GET    | `/api/quiz/history/{id}`    | Quiz history for user          |
| POST   | `/api/story/generate`       | Generate educational story      |
| POST   | `/api/tutor/learning-path`  | Generate learning path          |
| POST   | `/api/friend/chat`          | Chat with AI Friend            |
| POST   | `/api/ml/predict-performance`| Direct ML prediction          |
| POST   | `/api/ml/predict-sentiment`  | Direct sentiment analysis     |
| GET    | `/api/dashboard/stats/{id}` | Dashboard statistics            |

---

## ML Models

### Student Performance Prediction

- **Algorithm**: RandomForestClassifier (primary) vs LogisticRegression (comparison)
- **Dataset**: 2500 synthetic samples
- **Features**: quiz_accuracy, average_response_time, difficulty_level, number_of_attempts, topic_category
- **Target**: performance_level (low / medium / high)
- **Preprocessing**: LabelEncoder + StandardScaler
- **Output**: model.pkl (best performing model)

### Sentiment Analysis

- **Algorithm**: Naive Bayes (MultinomialNB)
- **Pipeline**: TF-IDF Vectorizer → MultinomialNB
- **Classes**: positive, neutral, stressed, anxious
- **Training data**: 80 labeled examples
- **Output**: sentiment_model.pkl

---

## UI Screenshots (Mock Layout)

### Dashboard
```
┌─────────────────────────────────────────────┐
│ ┌──────┐  ╔═══════════════════════════════╗ │
│ │ AI   │  ║  Dashboard                    ║ │
│ │ FOR  │  ║                               ║ │
│ │ EDU  │  ║  ┌─────┐ ┌─────┐ ┌─────┐     ║ │
│ │      │  ║  │  12  │ │ 78% │ │  5  │     ║ │
│ │ ──── │  ║  │Quiz  │ │Score│ │Chat │     ║ │
│ │▸Dash │  ║  └─────┘ └─────┘ └─────┘     ║ │
│ │ Pod  │  ║                               ║ │
│ │ Quiz │  ║  ╭─Performance Trend──────╮   ║ │
│ │ Story│  ║  │   ╱╲    ╱╲             │   ║ │
│ │ Tutor│  ║  │  ╱  ╲  ╱  ╲   ╱╲      │   ║ │
│ │ Friend│ ║  │ ╱    ╲╱    ╲ ╱  ╲     │   ║ │
│ │      │  ║  ╰────────────────────────╯   ║ │
│ └──────┘  ╚═══════════════════════════════╝ │
└─────────────────────────────────────────────┘
```

### Quiz Module
```
┌─────────────────────────────────────────────┐
│  AI Quiz                                     │
│  ────────────────────────────                │
│  Topic: [Photosynthesis    ] ▶ Generate      │
│  Difficulty: [Medium ▼]  Questions: [5 ▼]    │
│                                              │
│  ┌──Question 1/5─────────────────────────┐   │
│  │ What is the primary pigment in...?    │   │
│  │                                       │   │
│  │  [ A. Chlorophyll ]  [ B. Melanin  ]  │   │
│  │  [ C. Carotene   ]  [ D. Xanthophyll] │   │
│  └───────────────────────────────────────┘   │
│                                              │
│  ┌──AI Analysis──────────────────────────┐   │
│  │ Predicted: HIGH  │ Recommend: HARD    │   │
│  │ Weakness: 12%    │ Confidence: 89%    │   │
│  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### AI Friend Chat
```
┌─────────────────────────────────────────────┐
│  AI Friend  ♡                                │
│  ────────────────────────────                │
│                                              │
│  ┌─AI──────────────────────────────────┐     │
│  │ Hey! How are you doing today? 👋    │     │
│  └─────────────────────────────────────┘     │
│                                              │
│            ┌───────────────────────YOU─┐     │
│            │ I'm worried about my exam │     │
│            └──────────────────────────┘     │
│                                              │
│  ┌─AI──────────────────────────────────┐     │
│  │ I understand that feeling...        │     │
│  │ 😟 anxious (87%)                    │     │
│  └─────────────────────────────────────┘     │
│                                              │
│  ┌────────────────────────────────┐ [Send]   │
│  │ Type your message...           │          │
│  └────────────────────────────────┘          │
└─────────────────────────────────────────────┘
```

---

## Environment Variables

| Variable         | Description                  | Default              |
|-----------------|------------------------------|----------------------|
| `GEMINI_API_KEY` | Google Gemini API key        | (required)           |
| `DATABASE_URL`   | SQLite connection string     | `sqlite:///app.db`   |
| `HOST`           | Server host                  | `0.0.0.0`           |
| `PORT`           | Server port                  | `8000`              |
| `DEBUG`          | Enable debug mode            | `true`              |
| `FRONTEND_URL`   | Frontend URL for CORS        | `http://localhost:5173` |

---

## License

This project is built for educational purposes.

---

*Built with ♡ for learners everywhere.*
# aiforeducation
