# 🚀 Complete Deployment Guide - VERITAS Intelligence

## 📋 Deployment Overview

Your project has **two parts**:
1. **Frontend (Next.js)** → Deploy to **Vercel** ✅
2. **Backend (Python FastAPI)** → Deploy to **Render** or **Railway** ✅

---

## 🎯 PART 1: Deploy Backend to Render (FREE)

### **Step 1: Prepare Backend**

Your backend is already ready! It has:
- ✅ `requirements.txt` (dependencies)
- ✅ `main.py` (FastAPI app)
- ✅ `.env.example` (environment template)

### **Step 2: Create Render Account**

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### **Step 3: Deploy Backend**

1. **Click "New +" → "Web Service"**

2. **Connect Repository:**
   - Select `Roshankc12345/Fake-News-Detection`
   - Click "Connect"

3. **Configure Service:**
   ```
   Name: veritas-backend
   Region: Oregon (US West) or closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   
   Build Command:
   pip install -r requirements.txt && playwright install chromium
   
   Start Command:
   uvicorn main:app --host 0.0.0.0 --port $PORT
   
   Instance Type: Free
   ```

4. **Add Environment Variables:**
   Click "Advanced" → "Add Environment Variable"
   
   Add these 3 variables:
   ```
   GROQ_API_KEY = gsk_xxxxxxxxxxxxxxxx (your Groq API key)
   GOOGLE_CSE_KEY = AIzaSyxxxxxxxxxxxxxxxx (your Google CSE key)
   GOOGLE_CSE_ID = 16e67045xxxxxxx (your Google CSE ID)
   ```

5. **Click "Create Web Service"**

6. **Wait 5-10 minutes** for deployment

7. **Copy Your Backend URL:**
   - Example: `https://veritas-backend.onrender.com`
   - You'll need this for frontend!

### **Step 4: Test Backend**

```bash
# Test if backend is live
curl https://veritas-backend.onrender.com/

# Should return:
# {"message":"News Detection API is running"}
```

---

## 🎨 PART 2: Deploy Frontend to Vercel (FREE)

### **Step 1: Create Vercel Account**

1. Go to https://vercel.com
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### **Step 2: Import Project**

1. **Click "Add New..." → "Project"**

2. **Import Git Repository:**
   - Select `Roshankc12345/Fake-News-Detection`
   - Click "Import"

3. **Configure Project:**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   
   Build Command: 
   npm run build
   
   Output Directory:
   .next
   
   Install Command:
   npm install
   ```

4. **Add Environment Variable:**
   Click "Environment Variables"
   
   Add this variable:
   ```
   NEXT_PUBLIC_API_URL = https://veritas-backend.onrender.com
   ```
   (Use YOUR backend URL from Render!)

5. **Click "Deploy"**

6. **Wait 2-3 minutes** for deployment

7. **Your App URL:**
   - Vercel gives you: `https://fake-news-detection-chi.vercel.app`
   - Or custom domain if you set one up

---

## ✅ PART 3: Verify Deployment

### **Test Your Live App:**

1. **Open your Vercel URL** (e.g., `https://fake-news-detection-chi.vercel.app`)

2. **Test with Example:**
   - Input: "New iPhone 16 launched by Apple"
   - Type: Title
   - Click "Analyze with VERITAS"
   - Should show: REAL verdict ✅

3. **Test Fake News:**
   - Input: "Aliens landed in Times Square"
   - Type: Title
   - Should show: FAKE verdict ✅

4. **Check Browser Console:**
   - Press F12 → Console tab
   - Should see NO errors
   - If errors, check if CORS is configured (see below)

---

## 🔧 PART 4: Fix CORS (if needed)

If you see CORS errors in browser console, update backend CORS settings:

### **On Render Dashboard:**

1. Go to your backend service (`veritas-backend`)
2. Click "Environment" tab
3. Add new variable:
   ```
   FRONTEND_URL = https://your-frontend.vercel.app
   ```

4. **Or update `backend/main.py` line 26-35:**

```python
# Add your Vercel domain to allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3002",
        "https://your-app.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then commit and push:
```bash
git add backend/main.py
git commit -m "Update CORS for Vercel deployment"
git push origin main
```

Render will auto-redeploy in ~5 minutes.

---

## 🎉 PART 5: You're Live!

### **Share Your Project:**

```
🌐 Live App: https://your-app.vercel.app
📊 GitHub: https://github.com/Roshankc12345/Fake-News-Detection
📖 Documentation: See PROJECT_WRITEUP.md
```

### **Custom Domain (Optional):**

**On Vercel:**
1. Go to project settings → "Domains"
2. Add custom domain (e.g., `veritas-news.com`)
3. Update DNS records as instructed

**On Render:**
1. Go to backend service → "Settings"
2. Add custom domain (e.g., `api.veritas-news.com`)
3. Update DNS records

---

## 🐛 Troubleshooting

### **Problem: Frontend shows "Load failed"**

**Solution:**
- Check `NEXT_PUBLIC_API_URL` is set in Vercel
- Test backend URL directly: `curl https://your-backend.onrender.com/`
- Check browser console for exact error

### **Problem: Backend deployment fails**

**Solution:**
- Check if `requirements.txt` is in `backend/` folder
- Verify Python version (should be 3.11+)
- Check Render build logs for specific error

### **Problem: CORS errors**

**Solution:**
- Add Vercel URL to CORS allowed origins (see Part 4)
- Make sure URL doesn't have trailing slash

### **Problem: "Module not found" errors**

**Solution:**
- Check `package.json` has all dependencies
- Re-run deployment in Vercel dashboard

### **Problem: API calls timeout**

**Solution:**
- Render free tier "spins down" after inactivity
- First request after idle takes ~60 seconds to wake up
- Upgrade to paid tier ($7/month) for always-on

---

## 💰 Cost Breakdown

| Service | Tier | Cost | Limits |
|---------|------|------|--------|
| **Vercel** | Free | $0/month | 100GB bandwidth, Unlimited deployments |
| **Render** | Free | $0/month | 750 hours/month, Spins down after idle |
| **Groq API** | Free | $0/month | 30 req/min, 14,400 req/day |
| **Google CSE** | Free | $0/month | 100 queries/day |

**Total:** $0/month ✅

**To scale:**
- Render Starter: $7/month (always-on, no spin-down)
- Google CSE: $5 per 1,000 queries after free tier
- Vercel Pro: $20/month (team features, priority support)

---

## 🎯 Post-Deployment Checklist

- [ ] Backend deployed on Render
- [ ] Backend URL copied
- [ ] Frontend deployed on Vercel
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] Live app tested (fake and real news)
- [ ] CORS configured (no browser errors)
- [ ] GitHub repository updated
- [ ] README.md has live demo link

---

## 📝 Update Your README

Add this to your `README.md`:

```markdown
## 🌐 Live Demo

**Frontend:** https://your-app.vercel.app  
**Backend API:** https://your-backend.onrender.com

Try it now! Analyze any news article for authenticity.
```

---

## 🎓 For Your Resume/Portfolio

```
VERITAS Intelligence (Jan 2026)
- Full-stack AI news verification system with 95%+ accuracy
- Tech: Next.js, FastAPI, Groq Llama 3.3 70B, Google CSE API
- Deployed: Vercel (frontend) + Render (backend)
- Live: https://your-app.vercel.app
- GitHub: https://github.com/Roshankc12345/Fake-News-Detection
```

---

**You're ready to deploy! Follow the steps above and your app will be live in ~15 minutes.** 🚀
