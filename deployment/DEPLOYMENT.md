# Smart Learn – Deployment Guide

This guide outlines deployment options for production environments.

---

## 1. MongoDB Atlas Setup
1. Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a Database User with read/write credentials.
3. Under **Network Access**, add `0.0.0.0/0` (or specific deployment IP addresses).
4. Copy the MongoDB Connection String:
   `mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority`

---

## 2. Google Gemini API Key
1. Obtain an API Key from [Google AI Studio](https://aistudio.google.com/).
2. Keep `GEMINI_API_KEY` configured strictly on the backend environment.

---

## 3. Render / Railway Backend Deployment
1. Connect your GitHub repository to Render/Railway.
2. Select **Python Web Service**.
3. Build Command: `pip install -r backend/requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Configure Environment Variables:
   - `GEMINI_API_KEY`
   - `MONGODB_URI`
   - `MONGODB_DATABASE=smart_learn`
   - `JWT_SECRET`
   - `CORS_ORIGINS=https://your-frontend-domain.com`

---

## 4. Frontend Deployment (Vercel / Netlify / GitHub Pages)
1. In `frontend/js/api.js`, update `API_BASE_URL` to point to your deployed backend domain (e.g. `https://smart-learn-api.onrender.com`).
2. Deploy the `frontend/` folder as a static site.
