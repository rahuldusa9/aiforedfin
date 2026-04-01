# AI FOR EDUCATION - Technical Assets Pitch

## Product Snapshot
AI FOR EDUCATION is an adaptive learning platform that combines generative AI, classical machine learning, and interactive web experiences to support personalized student learning.

## Core Technical Assets

### Frontend Experience
- React (Vite) single-page application
- Tailwind CSS for fast, consistent UI styling
- Axios-based API client layer
- Modular page architecture for Dashboard, Quiz, Tutor, Story, Podcast, and AI Friend

### Backend Platform
- Python FastAPI REST backend
- Pydantic request and response validation
- Route-based service architecture (`routes/` + `services/`)
- CORS-enabled API integration for local and deployed frontend clients

### AI and Generative Intelligence
- Google Gemini API for:
- Quiz content generation
- Learning path generation
- Story generation
- Conversational AI Friend responses
- Prompt-engineered service layer in `gemini_service.py`

### Machine Learning Intelligence
- Scikit-learn models for adaptive behavior:
- Student performance prediction
- Sentiment analysis for emotional state detection
- Algorithms in use:
- RandomForestClassifier
- LogisticRegression (benchmark/comparison)
- Multinomial Naive Bayes (sentiment)
- TF-IDF vectorization + probability-based inference

### Data and Persistence
- MongoDB for application data storage
- Collections for:
- Users
- Quiz results
- Learning progress
- Emotional logs
- Structured model helper functions for document creation and serialization

### Audio and Media Stack
- Edge TTS for speech generation
- PyDub for post-processing and audio enhancement
- Static audio serving via FastAPI

## Engineering Assets

### Developer Productivity
- Batch scripts for quick local startup/shutdown
- Organized backend and frontend folder separation
- Environment-driven configuration with `.env`
- Auto-training workflow for ML artifacts when needed

### API and Integration Assets
- REST endpoints for auth, quiz, tutor, story, podcast, friend, dashboard, and ML prediction
- Swagger and ReDoc auto-generated docs from FastAPI
- Frontend API abstraction in `frontend/src/api.js`

## Differentiators
- Unified platform that combines:
- Content generation (LLM)
- Performance adaptation (ML)
- Emotional support (sentiment-aware chat)
- Multimodal learning output (text + audio)
- Education-specific architecture rather than a generic chatbot shell

## Pitch Value
This stack delivers a practical, scalable AI education product with a clear path from prototype to production: modern web UI, API-first backend, LLM-powered learning content, and ML-based personalization in one cohesive system.
