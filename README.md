# SMART LEARN – AI-POWERED LEARNING ASSISTANT

**Smart Learn** is a complete full-stack personalized learning and assessment web application powered by Google Gemini AI and MongoDB Atlas.

Students can extract transcripts from public educational YouTube videos, automatically generate custom MCQ test papers, attempt interactive quizzes, receive automatic evaluations, review detailed AI explanations, and obtain data-driven learning recommendations based on actual performance.

---

## 🌟 Key Features

1. **AI Question Answering**: Ask any educational question and get structured explanations with bulleted key takeaways.
2. **Concept Explanation**: Tailored breakdowns of educational concepts across **Beginner**, **Intermediate**, and **Advanced** levels with real-world analogies.
3. **Text Summarization**: Paste textbook chapters or articles to extract executive summaries, main points, core concepts, and key terms.
4. **YouTube-Based AI Test Generator**: Input single or multiple public YouTube URLs to generate custom MCQ tests (20, 40, 60, or 100 questions) across Easy, Medium, Hard, or Mixed difficulty levels.
5. **Interactive Test Attempt Engine**: Clean interface with question grid navigation, option selection, answered/unanswered tracking, and submission confirmation.
6. **Automatic Backend Scoring**: Ground-truth evaluation performed strictly on the backend to guarantee test integrity.
7. **Answer Review & AI Explanations**: Post-submission breakdown highlighting correct vs. student answers with step-by-step explanations.
8. **Reattempt & Practice Missed Questions**: Reattempt tests with fresh AI question sets or practice previously incorrect questions.
9. **Student Progress & Recommendations**: Analytics tracking tests attempted, average score, accuracy by difficulty level, and personalized AI study advice based on real performance.
10. **Secure JWT Authentication**: Real authentication with hashed passwords (bcrypt) and protected API endpoints.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, CSS3 (Modern Responsive Layout), Vanilla JavaScript (ES6+, Fetch API), FontAwesome 6.
* **Backend**: Python 3.10+, FastAPI, Uvicorn, Motor (Async MongoDB Driver), Pydantic v2.
* **Database**: MongoDB Atlas.
* **AI Engine**: Google Gemini API (`google-genai` / `google-generativeai`).
* **Transcript Extraction**: `youtube-transcript-api`.
* **Authentication**: JWT (JSON Web Tokens), `passlib` with `bcrypt`.

---

## 📁 Project Structure

```text
Smart-Learn/
│
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point & CORS configuration
│   │   ├── config.py             # App environment configuration settings
│   │   ├── database.py           # MongoDB connection & index creation
│   │   ├── models/               # Database document schema definitions
│   │   │   ├── user.py
│   │   │   ├── test.py
│   │   │   └── attempt.py
│   │   ├── schemas/              # Pydantic request & response schemas
│   │   │   ├── auth_schemas.py
│   │   │   ├── ai_schemas.py
│   │   │   ├── youtube_schemas.py
│   │   │   ├── test_schemas.py
│   │   │   └── progress_schemas.py
│   │   ├── routes/               # API route handlers
│   │   │   ├── auth.py           # Signup, login, me
│   │   │   ├── ai.py             # Question, explain, summarize
│   │   │   ├── youtube.py        # Transcript extraction
│   │   │   ├── tests.py          # Generate, submit, reattempt, practice
│   │   │   ├── attempts.py       # History & attempt details
│   │   │   └── progress.py       # Student progress & recommendations
│   │   ├── services/             # Core business & AI logic
│   │   │   ├── auth_service.py   # Hashing & JWT tokens
│   │   │   ├── youtube_service.py# YouTube transcript fetching & cleaning
│   │   │   └── gemini_service.py # Gemini API integration & MCQ generation
│   │   └── utils/
│   │       └── helpers.py
│   │
│   ├── requirements.txt          # Backend Python dependencies
│   └── .env.example              # Environment variables template
│
├── frontend/
│   ├── index.html                # Professional Landing Page
│   ├── login.html                # Student Login
│   ├── signup.html               # Account Registration
│   ├── dashboard.html            # Main Student Dashboard
│   ├── ask-ai.html               # AI Question Answering Tool
│   ├── explain.html              # Concept Explainer Tool
│   ├── summarize.html            # Text Summarizer Tool
│   ├── test-generator.html       # YouTube AI Test Generator Page
│   ├── test.html                 # Interactive Test Attempt Page
│   ├── results.html              # Automatic Score & Answer Review Page
│   ├── progress.html             # Progress Analytics & AI Advice
│   ├── history.html              # Past Test & Attempt History
│   ├── profile.html              # Student Profile
│   ├── css/
│   │   └── styles.css            # Responsive CSS stylesheet
│   └── js/
│       ├── api.js                # Central API fetch wrapper & auth handler
│       └── auth.js               # Auth protection & navigation manager
│
├── deployment/                   # Cloud deployment files & guides
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── render.yaml
│   └── DEPLOYMENT.md
│
├── .gitignore
└── README.md
```

---

## 🚀 Beginner Quick-Start Guide

Follow these simple steps to run Smart Learn on your local computer.

### Prerequisites
1. Install **Python 3.10+** from [python.org](https://www.python.org/).
2. Install **VS Code** (recommended editor).
3. Get a free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
4. Get a free **MongoDB Atlas URI** from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).

---

### Step 1: Extract & Open Project
1. Extract `Smart-Learn-AI-Powered-Learning-Assistant.zip`.
2. Open VS Code and open the extracted `Smart-Learn` folder.

---

### Step 2: Configure Environment Variables
1. Navigate to the `backend/` directory.
2. Duplicate `.env.example` and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in your actual credentials:
   ```env
   PORT=8000
   MONGODB_URI=mongodb+srv://your_username:your_password@cluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=smart_learn
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   JWT_SECRET=a_secure_random_secret_key_at_least_32_characters
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500
   ```

---

### Step 3: Set Up Backend Virtual Environment
Open a terminal inside VS Code and run:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

### Step 4: Run the Backend Server
Inside the `backend/` directory (with virtual environment activated):

```bash
uvicorn app.main:app --reload --port 8000
```

The backend server will start at `http://localhost:8000`. You can inspect the interactive API documentation at `http://localhost:8000/docs`.

---

### Step 5: Launch the Frontend
You can open the frontend in any web browser:

1. **Option A (VS Code Live Server - Recommended)**: Right-click `frontend/index.html` and click **"Open with Live Server"**.
2. **Option B (Python Simple HTTP Server)**:
   Open a new terminal window, navigate to `frontend/` and run:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   Open your browser at `http://localhost:3000`.

---

## 🔒 Security Practices
* **No Secret Exposure**: Gemini API Key and MongoDB credentials are stored strictly in backend `.env`.
* **Password Security**: Passwords are hashed using bcrypt before storing in MongoDB `users` collection.
* **Server-Side Scoring**: Score evaluation is performed exclusively by FastAPI backend logic.
* **JWT Protected Endpoints**: All student dashboard, test generation, and AI endpoints require a valid JWT token.

---

## 📄 License
This project is created for educational and learning purposes.
