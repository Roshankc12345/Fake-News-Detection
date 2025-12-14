# Production Deployment Checklist

## 🚀 Pre-Deployment Steps

### 1. Environment Variables Setup

**Backend (.env file):**
```bash
GROQ_API_KEY=your_actual_key
GOOGLE_CSE_KEY=your_actual_key  
GOOGLE_CSE_ID=your_actual_id
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

### 2. Update CORS in Backend

**File:** `backend/main.py` (Line 34)

**Change from:**
```python
allow_origins=["http://localhost:3000"]
```

**To:**
```python
allow_origins=[
    "http://localhost:3000",  # Local dev
    "https://your-frontend.vercel.app",  # Production
    "https://*.vercel.app",  # Preview deployments
]
```

### 3. Update API URL in Frontend

**Create:** `frontend/.env.local`
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 📋 Deployment Platforms

### **Backend: Render.com (Recommended)**

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Configure:
   - **Name**: fake-news-api
   - **Root Directory**: backend
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `python main.py`
   - **Plan**: Free

5. Add Environment Variables:
   - GROQ_API_KEY
   - GOOGLE_CSE_KEY
   - GOOGLE_CSE_ID

6. Deploy! Get URL like: `https://fake-news-api.onrender.com`

---

### **Frontend: Vercel (Recommended)**

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import GitHub repo
4. Configure:
   - **Framework**: Next.js (auto-detected)
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: .next

5. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`

6. Deploy! Get URL like: `https://fake-news-detection.vercel.app`

---

## ✅ Post-Deployment

1. Update backend CORS with your Vercel URL
2. Test the deployed app
3. Verify TTS, STT, and all features work

---

## 🔐 Security Checklist

- [ ] .env files in .gitignore
- [ ] API keys not in code
- [ ] CORS properly configured
- [ ] HTTPS enabled (automatic on Vercel/Render)

---

## 📊 Estimated Costs

**Free Tier (Perfect for demos):**
- Vercel: Free (100GB bandwidth)
- Render: Free (750 hours, sleeps after 15min)
- **Total: $0/month**

**Paid (Production):**
- Vercel Pro: $20/month
- Render Starter: $7/month
- **Total: $27/month**

---

Ready to deploy? Follow these steps in order! 🚀
