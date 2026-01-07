# 🔄 VERITAS Intelligence - Complete Workflow

## Simple Step-by-Step Project Workflow

---

## 📋 **Setup Workflow**

### **Initial Setup (One-time):**

```bash
# 1. Clone/Download Project
cd "Fake News /Fake-News-Detection"

# 2. Setup Backend
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
playwright install chromium

# 3. Configure Environment
cp .env.example .env
# Edit .env and add your API keys:
# - GROQ_API_KEY
# - GOOGLE_CSE_KEY  
# - GOOGLE_CSE_ID

# 4. Setup Frontend
cd ../frontend
npm install
```

---

## 🚀 **Daily Run Workflow**

### **Every time you want to run the project:**

#### **Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate    # Activate virtual environment
python main.py              # Start backend server
# ✅ Backend running on http://localhost:8000
```

#### **Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev                 # Start frontend dev server
# ✅ Frontend running on http://localhost:3000
```

#### **Browser:**
```
Open: http://localhost:3000
```

---

## 🔍 **User Interaction Workflow**

### **Step 1: User Opens Application**

```
Browser → http://localhost:3000
         ↓
    Loads React Frontend (Next.js)
         ↓
    Displays Input Interface
```

---

### **Step 2: User Enters News Content**

```
User chooses input type:
├─ URL Tab → Paste article link
├─ Title Tab → Enter headline
└─ Article Tab → Paste full text

User optionally enables features:
├─ ☑ TTS (Text-to-Speech)
└─ ☑ NER Reality Checker

User can also:
└─ 🎤 Click microphone for voice input
```

**Example Input:**
```
Type: Title
Content: "Venezuela President arrested by US Army"
Features: TTS ✓, NER ✓
```

---

### **Step 3: Frontend Sends Request to Backend**

```javascript
// Frontend (page.tsx)
User clicks "Analyze with VERITAS"
         ↓
Frontend creates JSON request:
{
  "content": "Venezuela President arrested by US Army",
  "input_type": "title",
  "enable_features": {
    "tts": true,
    "ner_reality_checker": true
  }
}
         ↓
POST http://localhost:8000/analyze
```

---

### **Step 4: Backend Processes Request**

```python
# Backend (main.py)

┌──────────────────────────────────────┐
│ 1. RECEIVE REQUEST                  │
│    - Validate input                 │
│    - Extract content & type         │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 2. CONTENT PREPROCESSING            │
│    IF URL:                          │
│      → Scrape with BeautifulSoup   │
│      → Extract title, author        │
│      → Generate AI summary          │
│    IF Title:                        │
│      → Search related news          │
│    ALWAYS:                          │
│      → Clean text                   │
│      → Normalize whitespace         │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 3. REAL-TIME WEB VERIFICATION       │
│    Query Google Custom Search:      │
│      → Get 10 search results        │
│    Filter credible sources:         │
│      → Check against 100+ domains   │
│      → BBC, Reuters, CNN, etc.      │
│    Calculate metrics:               │
│      → credible_count = 0           │
│      → credibility_ratio = 0%       │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 4. AI ANALYSIS                      │
│    Create enhanced prompt:          │
│      → Include content              │
│      → Add verification results     │
│      → Emphasize real-time data     │
│    Call Groq API:                   │
│      → Model: Llama 3.3 70B         │
│      → Temperature: 0.3             │
│    AI returns:                      │
│      → is_fake: true                │
│      → fake_probability: 92%        │
│      → real_probability: 8%         │
│      → red_flags: [...]             │
│      → reasoning: "..."             │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 5. SMART OVERRIDE LOGIC             │
│    Check credible_count:            │
│      credible_count = 0             │
│    Apply rule:                      │
│      "No credible sources"          │
│      → fake_prob += 10%             │
│    Final verdict:                   │
│      → is_fake: true                │
│      → fake_probability: 95%        │
│      → real_probability: 5%         │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 6. ADVANCED FEATURES (Optional)     │
│    IF TTS enabled:                  │
│      → Generate analysis summary    │
│      → Convert to MP3 (gTTS)        │
│      → Save to audio_files/         │
│    IF NER enabled:                  │
│      → Extract entities (BERT-NER)  │
│      → Verify via Google/Wikipedia  │
│      → Calculate credibility score  │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ 7. SEND RESPONSE                    │
│    Format JSON:                     │
│    {                                │
│      "is_fake": true,               │
│      "fake_probability": 95.0,      │
│      "real_probability": 5.0,       │
│      "red_flags": [...],            │
│      "reasoning": "...",            │
│      "advanced_features": {...}     │
│    }                                │
└──────────┬───────────────────────────┘
           ↓
    Return to Frontend
```

---

### **Step 5: Frontend Displays Results**

```typescript
// Frontend (page.tsx)

Receive JSON response
         ↓
Parse data
         ↓
┌──────────────────────────────────────┐
│ RENDER RESULTS                      │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  🚨 VERDICT CARD                │ │
│ │  ⚠️ Fake                        │ │
│ │  Confidence: 95%                │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  PROBABILITY BARS               │ │
│ │  Fake: ████████████████░░ 95%   │ │
│ │  Real: █░░░░░░░░░░░░░░░  5%    │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  🚩 RED FLAGS                   │ │
│ │  • No credible sources found    │ │
│ │  • Sensational claim            │ │
│ │  • No official statements       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  🧠 AI ANALYSIS                 │ │
│ │  No credible sources like BBC   │ │
│ │  or Reuters have reported...    │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  🔊 AUDIO PLAYER (if TTS on)    │ │
│ │  [▶️ Play Analysis]              │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  ✓ VERIFIED ENTITIES (if NER)   │ │
│ │  • Venezuela ✓ (LOC)            │ │
│ │  • US Army ✓ (ORG)              │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
         ↓
    User sees verdict
```

---

## 🎯 **Complete Example Workflow**

### **Real Example: Testing Fake News**

```
┌─────────────────────────────────────────────────────────┐
│ USER ACTION                                             │
├─────────────────────────────────────────────────────────┤
│ 1. Opens http://localhost:3000                         │
│ 2. Selects "Title" tab                                 │
│ 3. Types: "Venezuela President arrested by US Army"    │
│ 4. Enables: TTS ✓                                      │
│ 5. Clicks: "Analyze with VERITAS"                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ FRONTEND PROCESSING                                     │
├─────────────────────────────────────────────────────────┤
│ • Sets loading state (shows spinner)                   │
│ • Creates JSON payload                                 │
│ • POSTs to http://localhost:8000/analyze              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ BACKEND PROCESSING (5-15 seconds)                      │
├─────────────────────────────────────────────────────────┤
│ Phase 1: Google Search                                 │
│   → Searches: "Venezuela President arrested"           │
│   → Finds: 10 results                                  │
│   → Credible: 0 sources (no BBC, Reuters, CNN, etc.)   │
│   → Ratio: 0%                                          │
│                                                         │
│ Phase 2: AI Analysis                                   │
│   → Groq analyzes content + search results             │
│   → Returns: 92% fake, 8% real                         │
│   → Red flags: "No credible sources", "Sensational"    │
│                                                         │
│ Phase 3: Smart Override                                │
│   → credible_count = 0                                 │
│   → Applies: +10% to fake probability                  │
│   → Final: 95% fake, 5% real                           │
│                                                         │
│ Phase 4: TTS Generation                                │
│   → Creates summary: "Analysis Complete. Verdict..."   │
│   → Generates MP3 with gTTS                            │
│   → Saves to: backend/news_audio.mp3                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ FRONTEND DISPLAY                                        │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🚨 VERDICT: Fake                                    │ │
│ │ Confidence: 95%                                     │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ Fake: ████████████████████░ 95%                     │ │
│ │ Real: █░░░░░░░░░░░░░░░░░░░  5%                     │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ 🚩 Red Flags:                                       │ │
│ │  • No credible news sources report this             │ │
│ │  • Sensational claim lacks verification             │ │
│ │  • No official government statements                │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ 🧠 Reasoning:                                       │ │
│ │ "No credible sources like BBC or Reuters have       │ │
│ │  reported this claim. This is a sensational         │ │
│ │  statement that would be widely covered if true.    │ │
│ │  ⚠️ NO CREDIBLE SOURCES: Found 10 search results   │ │
│ │  but none from credible news organizations."        │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ 🔊 Audio: [▶️ Play] [⏸️ Pause]                      │ │
│ │ Duration: 0:45                                      │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ USER UNDERSTANDS                                        │
├─────────────────────────────────────────────────────────┤
│ ✅ Sees clear "FAKE" verdict                           │
│ ✅ Understands why (no credible sources)               │
│ ✅ Can verify reasoning independently                  │
│ ✅ Listens to audio explanation (accessibility)        │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 **Data Flow Summary**

```
User Input
    ↓
Frontend (Next.js)
    ↓
HTTP POST Request
    ↓
Backend API (FastAPI)
    ↓
┌─────────────────┐
│ Process Content │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Google Search   │ → External API call
└────────┬────────┘
         ↓
┌─────────────────┐
│ Filter Sources  │ → 100+ credible domains
└────────┬────────┘
         ↓
┌─────────────────┐
│ AI Analysis     │ → Groq Llama 3.3 70B
└────────┬────────┘
         ↓
┌─────────────────┐
│ Smart Override  │ → Evidence beats AI
└────────┬────────┘
         ↓
┌─────────────────┐
│ Generate TTS    │ → Optional: gTTS
└────────┬────────┘
         ↓
┌─────────────────┐
│ Extract Entities│ → Optional: BERT-NER
└────────┬────────┘
         ↓
JSON Response
    ↓
Frontend Rendering
    ↓
User Sees Results
```

---

## 🐛 **Troubleshooting Workflow**

### **Problem: Port 8000 already in use**

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 <PID>

# Or kill all on port 8000
lsof -ti:8000 | xargs kill -9

# Then restart backend
python main.py
```

### **Problem: Frontend can't connect to backend**

```bash
# Check backend is running
curl http://localhost:8000/

# Should return: {"message":"News Detection API is running"}

# If not, check if backend started successfully
# Look for: "INFO:     Uvicorn running on http://localhost:8000"
```

### **Problem: Module not found errors**

```bash
# Backend: Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend: Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📂 **File Structure Workflow**

```
Fake-News-Detection/
│
├── backend/                    # Python backend
│   ├── venv/                   # Virtual environment (IGNORED by git)
│   ├── main.py                 # Main FastAPI server
│   ├── advanced_features.py    # TTS, NER, etc.
│   ├── feature_config.py       # Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # API keys (IGNORED by git)
│   ├── .env.example            # Template for .env
│   └── news_audio.mp3          # Generated audio (IGNORED by git)
│
├── frontend/                   # Next.js frontend
│   ├── node_modules/           # Dependencies (IGNORED by git)
│   ├── app/
│   │   ├── page.tsx            # Main page component
│   │   ├── page.module.css     # Styling
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Global styles
│   ├── package.json            # Node dependencies
│   └── next.config.ts          # Next.js config
│
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
├── PROJECT_WRITEUP.md          # Academic write-up
├── PRESENTATION_GUIDE.md       # Presentation help
└── WORKFLOW.md                 # This file!
```

---

## 🚀 **Quick Start Workflow**

```bash
# 1. Start everything (2 terminals)

# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev

# 2. Open browser
# http://localhost:3000

# 3. Test with example
# Title: "New iPhone 16 launched by Apple"
# Should show: REAL (verified by multiple sources)

# 4. Test with fake news
# Title: "Aliens landed in Times Square"
# Should show: FAKE (no credible sources)
```

---

## ✅ **Workflow Checklist**

Before starting work:
- [ ] Backend virtual environment activated
- [ ] Backend server running on port 8000
- [ ] Frontend dev server running on port 3000
- [ ] `.env` file has valid API keys
- [ ] Browser open to localhost:3000

During development:
- [ ] Make code changes
- [ ] Backend: Restart `python main.py`
- [ ] Frontend: Hot reload (automatic)
- [ ] Test in browser
- [ ] Check console for errors

Before pushing to Git:
- [ ] `.env` files ignored (API keys protected)
- [ ] `venv/` and `node_modules/` ignored
- [ ] Large files (MP3, models) ignored
- [ ] Run `git status` to verify

---

**That's the complete workflow! Every step from setup to deployment.** 🎉
