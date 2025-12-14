# Deployment Guide - Fake News Detection System

**Last Updated:** December 15, 2025

---

## Table of Contents

1. [Quick Deploy (Easiest)](#quick-deploy-easiest)
2. [Prerequisites](#prerequisites)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Backend Deployment Options](#backend-deployment-options)
5. [Environment Variables](#environment-variables)
6. [Configuration Changes](#configuration-changes)
7. [Post-Deployment Testing](#post-deployment-testing)
8. [Troubleshooting](#troubleshooting)

---

## 1. Quick Deploy (Easiest)

**Recommended Stack:**
- **Frontend**: Vercel (Free tier, perfect for Next.js)
- **Backend**: Render or Railway (Free tier available)

**Total Time:** 15-20 minutes  
**Cost:** FREE (with limitations)

---

## 2. Prerequisites

### Required:
- ✅ GitHub account
- ✅ Groq API key (you already have this)
- ✅ Google Custom Search API key (you already have this)
- ✅ Your code pushed to GitHub

### Optional:
- Credit card (for some platforms, even on free tier)
- Domain name (for custom URLs)

### Push Your Code to GitHub:

```bash
# In your project root
cd "/Users/rohanlagarwar/Fake News /Fake-News-Detection"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Fake News Detection System"

# Create GitHub repository at github.com/new
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/fake-news-detection.git
git branch -M main
git push -u origin main
```

---

## 3. Frontend Deployment (Vercel)

### ⭐ Option 1: Vercel (Recommended - Easiest)

**Why Vercel?**
- Made by Next.js creators
- Automatic builds on git push
- Free SSL certificates
- Global CDN
- **FREE tier available**

### Step-by-Step:

#### 3.1 Sign Up & Connect

1. Go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Sign up with **GitHub**
4. Authorize Vercel to access your repositories

#### 3.2 Deploy Frontend

1. Click **"Add New Project"**
2. Select your **fake-news-detection** repository
3. Vercel will auto-detect it's a Next.js project

**Configure Project:**
```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

**Environment Variables:**
- None needed for frontend (API calls go to backend)

4. Click **"Deploy"**
5. Wait 2-3 minutes
6. You'll get a URL like: `https://fake-news-detection-xxxxx.vercel.app`

#### 3.3 Note Your Frontend URL

Save this URL - you'll need it for CORS configuration in the backend!

---

## 4. Backend Deployment Options

### ⭐ Option A: Render (Recommended)

**Free Tier:**
- 750 hours/month free
- Auto-sleeps after 15 min inactivity
- Wakes up on requests (cold start ~30s)

### Step-by-Step:

#### 4.1 Create `render.yaml`

Create this file in your **project root**:

```yaml
# render.yaml
services:
  - type: web
    name: fake-news-api
    env: python
    region: oregon
    plan: free
    buildCommand: "cd backend && pip install -r requirements.txt && playwright install chromium"
    startCommand: "cd backend && python main.py"
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: GOOGLE_CSE_KEY
        sync: false
      - key: GOOGLE_CSE_ID
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### 4.2 Deploy to Render

1. Go to [render.com](https://render.com)
2. Sign up with **GitHub**
3. Click **"New +"** → **"Web Service"**
4. Connect your repository
5. Render will detect `render.yaml`

**Configure:**
- **Name**: fake-news-api
- **Environment**: Python
- **Region**: Oregon (or closest to you)
- **Branch**: main
- **Root Directory**: Leave empty
- **Build Command**: `cd backend && pip install -r requirements.txt && playwright install chromium`
- **Start Command**: `cd backend && python main.py`

**Add Environment Variables:**
- `GROQ_API_KEY`: your_groq_api_key
- `GOOGLE_CSE_KEY`: your_google_key
- `GOOGLE_CSE_ID`: your_google_cse_id

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for first deploy
8. You'll get a URL like: `https://fake-news-api.onrender.com`

---

### Option B: Railway (Alternative)

**Free Tier:**
- $5 free credit/month
- No auto-sleep
- Faster than Render
- Credit card required

### Step-by-Step:

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository

**Configure:**
- **Root Directory**: `backend`
- **Start Command**: `python main.py`

**Add Environment Variables** (same as Render)

5. Deploy!

**URL**: `https://fake-news-api.up.railway.app`

---

### Option C: Google Cloud Run (Advanced)

**For production/scaling:**
- Pay per request
- Auto-scales
- No cold starts with min instances
- More complex setup

### Step-by-Step:

#### 4.3.1 Create Dockerfile

In `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

#### 4.3.2 Deploy to Cloud Run

```bash
# Install Google Cloud CLI
# Then:

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy fake-news-api \
  --source ./backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key,GOOGLE_CSE_KEY=your_key,GOOGLE_CSE_ID=your_id
```

---

## 5. Environment Variables

### Backend Environment Variables:

```bash
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
GOOGLE_CSE_KEY=AIzaSyxxxxxxxxxx
GOOGLE_CSE_ID=16e67045xxxxx

# Optional (for performance)
HF_DEVICE=cpu
PIPELINE_CACHE_MAX=2
FEATURE_TIMEOUT=15
```

### Frontend Environment Variables:

```bash
# Next.js (if needed)
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

---

## 6. Configuration Changes

### 6.1 Update CORS in Backend

**File:** `backend/main.py` (Line 32-38)

**Before:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**After:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://your-frontend.vercel.app",  # Replace with your Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6.2 Update API URL in Frontend

**File:** `frontend/app/page.tsx` (Line 87)

**Before:**
```typescript
const response = await fetch('http://localhost:8000/analyze', {
```

**After:**
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const response = await fetch(`${apiUrl}/analyze`, {
```

**Then add to Vercel:**
- Environment Variable: `NEXT_PUBLIC_API_URL`
- Value: `https://your-backend.onrender.com`

### 6.3 Update Audio URL

**File:** `frontend/app/page.tsx` (Line 436)

**Before:**
```typescript
src={`http://localhost:8000${result.advanced_features.tts.url}`}
```

**After:**
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
src={`${apiUrl}${result.advanced_features.tts.url}`}
```

---

## 7. Post-Deployment Testing

### 7.1 Test Backend Health

```bash
curl https://your-backend.onrender.com/
# Should return: {"message":"News Detection API is running"}
```

### 7.2 Test Frontend

1. Visit your Vercel URL
2. Paste a news URL (e.g., BBC article)
3. Click "Analyze"
4. Should see results in 5-15 seconds

### 7.3 Test Full Flow

Try these test cases:

**Real News:**
- https://www.bbc.com/news (any recent article)
- https://techcrunch.com (any tech news)

**Fake News Test:**
- Make up a sensational headline
- Copy text from a satirical site

---

## 8. Troubleshooting

### Issue: CORS Error

**Error:** `Access to fetch blocked by CORS policy`

**Fix:**
1. Update `allow_origins` in `backend/main.py`
2. Add your Vercel URL
3. Redeploy backend

### Issue: 500 Internal Server Error

**Error:** Backend crashes on requests

**Fix:**
1. Check backend logs in Render/Railway dashboard
2. Likely missing environment variables
3. Add all required env vars

### Issue: Cold Start Timeout

**Error:** Request times out on first request

**Fix:**
- Free tier backends sleep after inactivity
- First request takes 30-60 seconds (cold start)
- Subsequent requests are fast
- Upgrade to paid tier for no cold starts

### Issue: Playwright/Browser Error

**Error:** `Browser not found`

**Fix:**
Add to build command:
```bash
playwright install chromium
playwright install-deps chromium
```

### Issue: Audio Not Playing

**Error:** Audio player shows but doesn't play

**Fix:**
1. Check audio URL in browser console
2. Ensure CORS allows audio requests
3. Test: `https://your-backend.onrender.com/audio/news_audio.mp3`

### Issue: Large Audio Files Fail

**Error:** Audio generation times out

**Fix:**
- Free tier has memory limits
- Reduce max words in TTS (backend/advanced_features.py line 202)
- Change from 500 to 300 words

---

## 9. Production Optimization

### For Better Performance:

1. **Enable Caching:** Add Redis for result caching
2. **Database:** Store analysis history in PostgreSQL
3. **CDN:** Use Cloudflare for static assets
4. **Monitoring:** Add Sentry for error tracking
5. **Rate Limiting:** Prevent API abuse

### Recommended Upgrades:

**Free Tier Limitations:**
- Render: Sleeps after 15 min → $7/month for always-on
- Railway: $5/month credit → $5-20/month based on usage
- Vercel: Unlimited frontend deployments (free)

**Paid Production Setup ($20-50/month):**
- Frontend: Vercel Pro ($20/month) - more bandwidth
- Backend: Render Starter ($7/month) - no sleep
- Database: Render PostgreSQL ($7/month) - for history
- Redis: Render Redis ($10/month) - for caching

---

## 10. Quick Reference

### Deployment Checklist:

- [ ] Code pushed to GitHub
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render/Railway
- [ ] Environment variables configured
- [ ] CORS updated in backend
- [ ] API URL updated in frontend
- [ ] Test with real news article
- [ ] Test with fake news
- [ ] Test TTS feature
- [ ] Test NER feature

### URLs After Deployment:

```
Frontend: https://fake-news-detection-xxxxx.vercel.app
Backend:  https://fake-news-api.onrender.com
GitHub:   https://github.com/YOUR_USERNAME/fake-news-detection
```

---

## 11. Free Tier Summary

| Service | Free Tier | Limits | Best For |
|---------|-----------|--------|----------|
| **Vercel** | ✅ Unlimited | 100GB bandwidth/month | Frontend |
| **Render** | ✅ 750 hrs/month | Sleeps after 15 min | Backend |
| **Railway** | ✅ $5 credit/month | ~500 hrs equivalent | Backend |
| **Netlify** | ✅ Unlimited | 100GB bandwidth/month | Frontend alternative |

**Total Cost for Free Deployment: $0/month** 🎉

---

## 12. Next Steps

After deployment:

1. **Custom Domain:** Buy domain, connect to Vercel
2. **Analytics:** Add Google Analytics
3. **Monitoring:** Set up error tracking (Sentry)
4. **Performance:** Add caching layer (Redis)
5. **Features:** Add user accounts, history
6. **Scale:** Upgrade to paid tiers when needed

---

## Need Help?

**Common Issues:** See Troubleshooting section above  
**Platform Docs:**
- Vercel: https://vercel.com/docs
- Render: https://render.com/docs
- Railway: https://docs.railway.app

**Contact:** Open an issue on GitHub

---

**Good luck with your deployment! 🚀**
