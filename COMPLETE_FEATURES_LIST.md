# Complete Features List - Fake News Detection System

**Project:** VERITAS Intelligence  
**Date:** December 15, 2025  
**Purpose:** Document all features for replication

---

## Table of Contents

1. [Core Features](#core-features)
2. [Input Processing](#input-processing)
3. [AI Analysis](#ai-analysis)
4. [Verification System](#verification-system)
5. [Advanced NLP Features](#advanced-nlp-features)
6. [UI/UX Features](#uiux-features)
7. [API Features](#api-features)
8. [Technical Features](#technical-features)

---

## 1. Core Features

### ✅ 1.1 Multi-Input Analysis

**What it does:** Accepts 3 different types of news content

**Types:**
1. **URL** - Paste article link
2. **Title** - Just the headline
3. **Full Article** - Copy-paste entire text

**Implementation:**
```typescript
// Frontend: page.tsx (Lines 67-74)
const [inputType, setInputType] = useState<'title' | 'url' | 'article'>('url');
const [featureToggles, setFeatureToggles] = useState({
  tts: false,
  ner_reality_checker: false,
});
```

**How to replicate:**
- Use React useState for input type selection
- Three tab buttons for switching
- Dynamic textarea placeholder based on type
- Send `input_type` in API request

---

### ✅ 1.2 Real-Time Fake News Detection

**What it does:** Analyzes content and returns verdict with probability scores

**Output:**
- **is_fake**: Boolean (True/False)
- **fake_probability**: 0-100%
- **real_probability**: 0-100%
- **confidence_score**: How sure the system is

**Implementation:**
```python
# Backend: main.py (Lines 637-655)
confidence_score = max(fake_prob, real_prob)  # Higher probability = confidence

return AnalysisResult(
    is_fake=bool(analysis.get("is_fake", fake_prob > 50)),
    fake_probability=round(fake_prob, 2),
    real_probability=round(real_prob, 2),
    confidence_score=round(confidence_score, 2),
    # ... other fields
)
```

**How to replicate:**
- Normalize probabilities to sum to 100%
- Use max() for confidence (not difference)
- Round to 2 decimal places
- Return structured JSON

---

## 2. Input Processing

### ✅ 2.1 URL Article Extraction

**What it does:** Visits URL, extracts article content and metadata

**Extracted Data:**
- Title
- Author  
- Source/Publisher
- Article body text
- URL

**Implementation:**
```python
# Backend: main.py (Lines 142-215)
async def extract_article_from_url(url: str) -> tuple[str, ArticleMetadata]:
    # 1. HTTP GET with User-Agent
    headers = {"User-Agent": "Mozilla/5.0 ..."}
    resp = requests.get(url, headers=headers, timeout=20)
    
    # 2. Parse HTML
    soup = BeautifulSoup(resp.text, "lxml")
    
    # 3. Remove junk
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    
    # 4. Extract metadata
    title = soup.title.string or meta("og:title")
    author = meta("author") or find(class_="author")
    source = meta("og:site_name") or domain
    
    # 5. Find article content
    selectors = ["article", ".article-content", "main"]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and len(el.get_text()) > 100:
            content = el.get_text()
            break
    
    # 6. Clean whitespace
    content = re.sub(r"\s+", " ", content).strip()
    
    return content[:15000], metadata
```

**How to replicate:**
- Use `requests` with browser User-Agent
- Parse with `BeautifulSoup` + `lxml`
- Try multiple CSS selectors
- Extract OpenGraph meta tags
- Clean whitespace with regex
- Limit to 15,000 characters

---

### ✅ 2.2 Content Cleaning

**What it does:** Removes URLs, extra spaces, non-article content

**Implementation:**
```python
# Backend: advanced_features.py (Lines 22-25)
def _clean_text(text: str, limit: int = 12000) -> str:
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
    return text[:limit]
```

**How to replicate:**
- Regex to remove URLs
- Replace multiple spaces with single space
- Add character limit

---

## 3. AI Analysis

### ✅ 3.1 Groq Llama 3.3 70B Integration

**What it does:** Uses advanced LLM to analyze news content

**API Call:**
```python
# Backend: main.py (Lines 575-590)
chat_completion = groq_client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a professional fact-checker..."
        },
        {
            "role": "user",
            "content": prompt  # Includes article + Google verification
        }
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.3,  # Low for consistency
    max_tokens=2000,
)
```

**How to replicate:**
- Install: `pip install groq`
- Get API key from groq.com
- Low temperature (0.3) for factual analysis
- System prompt defines role
- Parse JSON from response

---

### ✅ 3.2 Smart Prompt Engineering

**What it does:** Crafts prompts with context for better analysis

**For Titles:**
```python
# Backend: main.py (Lines 484-516)
prompt = f"""
Title: "{content}"

Related sources found:
{sources_info}

🔍 REAL-TIME GOOGLE SEARCH VERIFICATION:
- Total results: {total_results}
- Credible sources: {credible_count}
- Credibility ratio: {ratio}%

CRITICAL: If 2+ credible sources (BBC, Reuters, CNN) report this,
mark as REAL. Trust Google Search over training data.

Respond in JSON format:
{{
    "is_fake": boolean,
    "fake_probability": float,
    "real_probability": float,
    "red_flags": [...],
    "patterns": [...],
    "reasoning": "...",
    "key_entities": [...]
}}
"""
```

**How to replicate:**
- Include Google verification results in prompt
- Emphasize real-time data > training data
- List credible sources explicitly
- Request structured JSON output
- Add context from related sources

---

### ✅ 3.3 JSON Response Parsing

**What it does:** Extracts JSON from AI response (handles markdown)

**Implementation:**
```python
# Backend: main.py (Lines 595-608)
response_text = chat_completion.choices[0].message.content.strip()

# Handle markdown code blocks
if "```json" in response_text:
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(1)
elif "```" in response_text:
    json_match = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(1)
else:
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group()

analysis = json.loads(response_text)
```

**How to replicate:**
- Try extracting from ```json blocks first
- Fallback to ``` blocks
- Final fallback: find any JSON object
- Use regex with DOTALL flag
- Handle parse errors gracefully

---

## 4. Verification System

### ✅ 4.1 Google Custom Search Integration

**What it does:** Searches Google to verify if credible sources report the news

**Implementation:**
```python
# Backend: main.py (Lines 302-451)
async def verify_with_google_search(query: str, max_results: int = 10):
    api_key = os.getenv("GOOGLE_CSE_KEY")
    cx = os.getenv("GOOGLE_CSE_ID")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": max_results}
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        items = data.get("items", [])
        
        # Check each result against credible domains
        credible_sources = []
        for item in items:
            domain = item.get("displayLink", "").lower()
            if any(cred in domain for cred in credible_domains):
                credible_sources.append(item)
        
        return {
            "total_results": len(items),
            "credible_results": len(credible_sources),
            "search_results": items[:5],
            "credible_sources": credible_sources[:5],
            "verification_summary": {
                "found_sources": len(items) > 0,
                "has_credible_sources": len(credible_sources) > 0,
                "credibility_ratio": len(credible_sources) / len(items)
            }
        }
```

**How to replicate:**
- Get Google Custom Search API key
- Create Custom Search Engine
- Use async httpx for requests
- Check domain against credible list
- Calculate credibility ratio
- Timeout after 15 seconds

---

### ✅ 4.2 Credible Domains List (100+ sources)

**What it does:** Maintains list of trustworthy news outlets

**Categories:**
```python
# Backend: main.py (Lines 388-438)
credible_domains = [
    # International: BBC, CNN, Reuters, AP, Bloomberg
    'bbc.', 'cnn.', 'reuters.', 'apnews.', 'bloomberg.',
    
    # US News: NYT, WaPo, WSJ, NPR
    'nytimes.', 'washingtonpost.', 'wsj.', 'npr.org',
    
    # UK: Guardian, Telegraph
    'theguardian.', 'telegraph.co.uk',
    
    # Indian: Hindu, NDTV, TOI, LiveMint, Economic Times
    'thehindu.', 'ndtv.', 'livemint.', 'economictimes.',
    
    # Indian Business: Finshots, The Ken, Inc42
    'finshots.in', 'theken.in', 'inc42.com',
    
    # Tech: TechCrunch, The Verge, Wired, Ars Technica
    'techcrunch.', 'theverge.', 'wired.', 'arstechnica.',
    
    # Music/Entertainment: Billboard, Rolling Stone, Variety
    'billboard.', 'rollingstone.', 'variety.',
    
    # Official Blogs: Google, Microsoft, Apple, Meta, Spotify
    'blog.google', 'blogs.microsoft.', 'newsroom.apple.',
    'newsroom.spotify.', 'blog.youtube',
    
    # Academic: Nature, Science, arXiv
    'nature.com', 'sciencemag.org', 'arxiv.org',
    
    # Business: FT, CNBC, Business Insider
    'ft.com', 'cnbc.', 'businessinsider.',
]
```

**How to replicate:**
- Create comprehensive list
- Use partial matches (.com, .co.uk, etc.)
- Categorize by type
- Include regional sources
- Add company blogs
- Include academic sources

---

### ✅ 4.3 Smart Override Logic

**What it does:** Overrides AI verdict when strong evidence exists

**Implementation:**
```python
# Backend: main.py (Lines 738-789)
if google_verification:
    credible_count = google_verification.get('credible_results', 0)
    credibility_ratio = verification_summary.get('credibility_ratio', 0)
    
    # Strong evidence: 3+ credible sources
    if credible_count >= 3 and credibility_ratio >= 0.3:
        result.is_fake = False
        result.real_probability = min(95.0, 60.0 + (credible_count * 7))
        result.fake_probability = 100.0 - result.real_probability
        result.reasoning += f"\n\n✅ VERIFICATION OVERRIDE: Found {credible_count} credible sources..."
    
    # Moderate: 1-2 credible sources
    elif credible_count >= 1 and credible_count < 3:
        adjustment = credible_count * 15  # 15% per source
        result.real_probability = min(80.0, result.real_probability + adjustment)
        result.fake_probability = 100.0 - result.real_probability
        result.reasoning += f"\n\n⚖️ PROBABILITY ADJUSTED: +{adjustment}%"
    
    # No credible sources
    elif total_results >= 5 and credible_count == 0:
        result.fake_probability = min(95.0, result.fake_probability + 10)
        result.real_probability = 100.0 - result.fake_probability
        result.is_fake = True
        result.reasoning += "\n\n⚠️ NO CREDIBLE SOURCES FOUND"
```

**How to replicate:**
- Check credible source count
- 3+ sources → Override to REAL (95% confidence)
- 1-2 sources → Adjust +15% per source
- 0 sources → Warning, increase fake probability
- Update reasoning with explanation
- Recalculate probabilities

---

### ✅ 4.4 GNews API Integration

**What it does:** Searches news aggregator for related articles

**Implementation:**
```python
# Backend: main.py (Lines 217-229)
async def search_news_title(title: str) -> List[dict]:
    google_news = GNews(language='en', max_results=5)
    results = google_news.get_news(title)
    
    # Optionally add Google CSE results
    extra = await search_google_cse(title, max_results=4)
    merged = merge_deduplicate_results(results, extra)
    return merged
```

**How to replicate:**
- Install: `pip install gnews`
- Create GNews instance
- Search by title or keywords
- Merge with Google CSE results
- Deduplicate by URL

---

## 5. Advanced NLP Features

### ✅ 5.1 Text-to-Speech (TTS)

**What it does:** Converts article to audio (MP3)

**Implementation:**
```python
# Backend: advanced_features.py (Lines 180-231)
def tts_generate(text: str, filename: str = "news_audio.mp3"):
    from gtts import gTTS
    
    # 1. Clean text (remove ads, URLs)
    text = _clean_text_for_tts(text)
    
    # 2. Limit to 500 words
    words = text.split()
    if len(words) > 500:
        text = ' '.join(words[:500]) + "."
    
    # 3. Generate audio
    tts = gTTS(text=text, lang='en', slow=False)
    filepath = os.path.join(AUDIO_DIR, filename)
    tts.save(filepath)
    
    # 4. Return URL
    return {"ok": True, "url": f"/audio/{filename}"}
```

**Cleaning Function:**
```python
# Backend: advanced_features.py (Lines 95-177)
def _clean_text_for_tts(text: str) -> str:
    # Remove URLs and emails
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove noise patterns
    noise_patterns = [
        r'click\s+here', r'subscribe\s+now', r'sign\s+up',
        r'facebook|twitter|instagram',
        r'copyright\s+©?\s*\d{4}',
    ]
    for pattern in noise patterns:
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    
    # Filter lines
    lines = text.split('\n')
    content_lines = []
    for line in lines:
        if len(line) < 15: continue  # Too short
        if re.match(r'^[\d\s\-/:,°]+$', line): continue  # Pure numbers
        if line.lower().startswith(('menu', 'search', 'login')): continue
        content_lines.append(line)
    
    # Extract sentences
    text = ' '.join(content_lines)
    sentences = re.split(r'[.!?]+\s+', text)
    good_sentences = [s for s in sentences if len(s) >= 15 and len(s.split()) >= 3]
    
    return '. '.join(good_sentences[:30])
```

**How to replicate:**
- Install: `pip install gtts`
- Clean text thoroughly
- Limit to 500 words max
- Save as MP3
- Return streaming URL

---

### ✅ 5.2 Named Entity Recognition (NER)

**What it does:** Extracts people, organizations, locations from text

**Implementation:**
```python
# Backend: advanced_features.py (Lines 297-388)
def ner_reality_checker(text: str):
    # 1. Load BERT-NER model (cached)
    ner = _safe_pipeline("ner", "dslim/bert-base-NER", device="cpu")
    
    # 2. Extract entities
    entities_raw = ner(text)
    
    # 3. Filter and clean
    entities = []
    seen = set()
    for ent in entities_raw:
        label = ent.get("entity_group")  # PER, ORG, LOC
        text_val = ent.get("word").strip()
        
        # Only keep meaningful entities
        if label not in ["PER", "ORG", "LOC"]: continue
        if len(text_val) < 3: continue
        if text_val.lower() in exclude_words: continue
        if text_val.lower() in seen: continue
        
        seen.add(text_val.lower())
        
        # 4. Verify via Google or Wikipedia
        verification = _verify_entity_google(text_val, label)
        
        if verification.get("verified"):
            entities.append({
                "text": text_val,
                "label": label,
                "verified": True,
                "status": "verified via Google" or "verified via Wikipedia",
                "source": verification.get("source")
            })
    
    # 5. Calculate credibility
    credibility_score = 100 if len(entities) > 0 else 0
    
    return {"ok": True, "entities": entities, "credibility_score": score}
```

**Entity Verification:**
```python
# Backend: advanced_features.py (Lines 256-294)
def _verify_entity_google(query: str, entity_type: str) -> dict:
    # Try Google Custom Search
    api_key = os.getenv("GOOGLE_CSE_KEY")
    cx = os.getenv("GOOGLE_CSE_ID")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": 3}
    
    resp = requests.get(url, params=params, timeout=5)
    data = resp.json()
    items = data.get("items", [])
    
    # Check for credible domains
    credible_count = 0
    for item in items:
        domain = item.get("displayLink", "").lower()
        if any(d in domain for d in ["wikipedia", ".gov", ".edu", "britannica"]):
            credible_count += 1
    
    if len(items) >= 2 and credible_count >= 1:
        return {"verified": True, "source": "google_search"}
    
    # Fallback to Wikipedia
    return {"verified": _wiki_exists(query), "source": "wikipedia"}
```

**How to replicate:**
- Install: `pip install transformers torch`
- Use BERT-NER model: `dslim/bert-base-NER`
- Extract PER, ORG, LOC entities
- Verify each via Google/Wikipedia
- Filter noise and duplicates
- Calculate credibility score

---

### ✅ 5.3 Model Caching

**What it does:** Caches ML models to avoid reloading

**Implementation:**
```python
# Backend: advanced_features.py (Lines 236-239)
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_ner():
    cfg = get_config()
    return _safe_pipeline("ner", cfg["models"]["ner"], device="cpu")
```

**How to replicate:**
- Use `@lru_cache(maxsize=1)`
- Lazy load models (only when first called)
- Return cached instance on subsequent calls

---

## 6. UI/UX Features

### ✅ 6.1 Glassmorphism Design

**What it does:** Creates modern, premium UI with glass effect

**Implementation:**
```css
/* Frontend: page.module.css */
.card {
  background: rgba(20, 20, 30, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}
```

**How to replicate:**
- Use `backdrop-filter: blur()`
- Semi-transparent backgrounds
- Subtle borders
- Rounded corners

---

### ✅ 6.2 Animated Gradient Blobs

**What it does:** Adds floating gradient backgrounds

**Implementation:**
```css
/* Frontend: page.module.css */
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

.blob {
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(20, 241, 215, 0.15), transparent);
  border-radius: 50%;
  filter: blur(60px);
  animation: float 20s ease-in-out infinite;
}
```

**How to replicate:**
- Create gradient circles
- Add blur filter  
- Animate with CSS keyframes
- Position absolute
- Multiple blobs with delays

---

### ✅ 6.3 Dynamic Probability Bars

**What it does:** Animated progress bars for fake/real percentages

**Implementation:**
```tsx
{/* Frontend: page.tsx (Lines 336-366) */}
<div className={styles.probabilityGrid}>
  <div className={styles.probabilityCard}>
    <div className={styles.probabilityHeader}>
      <span>Fake</span>
      <span>{result.fake_probability.toFixed(1)}%</span>
    </div>
    <div className={styles.probabilityTrack}>
      <div 
        className={styles.probabilityBar}
        style={{ width: `${result.fake_probability}%` }}
      />
    </div>
  </div>
</div>
```

**How to replicate:**
- Create track background
- Add filled bar with dynamic width
- Use inline style for percentage
- Add CSS transitions for animation

---

### ✅ 6.4 Conditional Color Coding

**What it does:** Shows red for fake, green for real

**Implementation:**
```tsx
{/* Frontend: page.tsx (Lines 309-367) */}
<div className={`
  ${styles.verdictCard} 
  ${result.is_fake ? styles.verdictFake : styles.verdictReal}
`}>
  {result.is_fake ? (
    <AlertTriangle />  // Red warning icon
  ) : (
    <CheckCircle />    // Green check icon
  )}
  <div className={styles.verdictTitle}>
    {result.is_fake
      ? result.fake_probability >= 80 ? 'Fake' : 'Likely Fake'
      : result.real_probability >= 80 ? 'Real' : 'Likely Real'}
  </div>
</div>
```

**How to replicate:**
- Conditional className based on verdict
- Different icons for fake/real
- Color-coded backgrounds

---

### ✅ 6.5 Loading States

**What it does:** Shows spinner during analysis

**Implementation:**
```tsx
{/* Frontend: page.tsx (Lines 232-249) */}
<button 
  onClick={analyzeNews}
  disabled={loading || !content.trim()}
  className={styles.primaryButton}
>
  {loading ? (
    <span className={styles.buttonContent}>
      <Loader2 className="animate-spin" />
      Analyzing...
    </span>
  ) : (
    <span className={styles.buttonContent}>
      <Search />
      Analyze with VERITAS
    </span>
  )}
</button>
```

**How to replicate:**
- Boolean loading state
- Conditional rendering
- Spinning loader icon
- Disable button while loading

---

### ✅ 6.6 Feature Toggles

**What it does:** Checkboxes to enable optional features

**Implementation:**
```tsx
{/* Frontend: page.tsx (Lines 216-229) */}
<div className={styles.featureToggleGrid}>
  {Object.entries(featureToggles).map(([key, value]) => (
    <label key={key} className={styles.featureToggle}>
      <input
        type="checkbox"
        checked={value}
        onChange={(e) =>
          setFeatureToggles((prev) => ({ ...prev, [key]: e.target.checked }))
        }
      />
      <span>{key.replace(/_/g, ' ')}</span>
    </label>
  ))}
</div>
```

**How to replicate:**
- Object for toggle states
- Map over entries
- Checkbox inputs
- Update state on change
- Send to API in request

---

## 7. API Features

### ✅ 7.1 FastAPI Backend

**What it does:** High-performance async Python API

**Implementation:**
```python
# Backend: main.py (Lines 1-25)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="News Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**How to replicate:**
- Install: `pip install fastapi uvicorn`
- Create FastAPI instance
- Add CORS middleware
- Define routes with decorators

---

### ✅ 7.2 Pydantic Models

**What it does:** Type validation and auto-documentation

**Implementation:**
```python
# Backend: main.py (Lines 116-140)
from pydantic import BaseModel
from typing import Optional, List

class NewsRequest(BaseModel):
    content: str
    input_type: str  # "title", "url", or "article"
    enable_features: Optional[dict] = None

class ArticleMetadata(BaseModel):
    title: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None

class AnalysisResult(BaseModel):
    is_fake: bool
    fake_probability: float
    real_probability: float
    confidence_score: float
    red_flags: List[str]
    patterns: List[str]
    reasoning: str
    # ... more fields
```

**How to replicate:**
- Import BaseModel from pydantic
- Define class with type hints
- Use Optional for nullable fields
- FastAPI auto-validates

---

### ✅ 7.3 HTTP Range Requests for Audio

**What it does:** Enables audio streaming and seeking

**Implementation:**
```python
# Backend: main.py (Lines 47-114)
@app.get("/audio/{filename}")
async def serve_audio(filename: str, request: Request):
    range_header = request.headers.get("range")
    file_size = os.path.getsize(filepath)
    
    if not range_header:
        return FileResponse(filepath, media_type="audio/mpeg")
    
    # Parse range (e.g., "bytes=0-1023")
    start, end = parse_range(range_header, file_size)
    
    # Stream chunk
    def file_iterator():
        with open(filepath, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                data = f.read(min(8192, remaining))
                remaining -= len(data)
                yield data
    
    return StreamingResponse(
        file_iterator(),
        status_code=206,  # Partial Content
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        }
    )
```

**How to replicate:**
- Parse Range header
- Return 206 status code
- Stream file chunks
- Set Content-Range header
- Support seeking in audio player

---

### ✅ 7.4 Async Operations

**What it does:** Runs Google Search and AI concurrently

**Implementation:**
```python
# Backend: main.py (Lines 717-735)
# Run Google verification in background
google_verification = await verify_with_google_search(query, max_results=10)

# Analyze with Groq (happens after Google search completes)
result = await analyze_with_groq(content, input_type, sources, google_verification)

# Run optional features concurrently
if request.enable_features:
    adv = await run_selected_features(content, selection)
    result.advanced_features = adv
```

**How to replicate:**
- Use `async def` for functions
- Use `await` for async operations
- Use `asyncio.gather()` for concurrent tasks
- Return awaitable coroutines

---

## 8. Technical Features

### ✅ 8.1 Environment Variables

**What it does:** Secure API key storage

**Implementation:**
```python
# Backend: main.py (Lines 6, 19, 41)
from dotenv import load_dotenv
import os

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
api_key = os.getenv("GOOGLE_CSE_KEY")
```

**How to replicate:**
- Create `.env` file (add to `.gitignore`)
- Install: `pip install python-dotenv`
- Load at app start
- Access with `os.getenv()`

---

### ✅ 8.2 Error Handling

**What it does:** Graceful degradation on failures

**Implementation:**
```python
# Backend: main.py (Lines 651-657)
try:
    analysis = json.loads(response_text)
except json.JSONDecodeError as e:
    raise HTTPException(
        status_code=500,
        detail=f"Failed to parse AI response: {response_text[:200]}"
    )
```

**How to replicate:**
- Try-except blocks
- Raise HTTPException for API errors
- Return structured error messages
- Log errors for debugging

---

### ✅ 8.3 Timeout Handling

**What it does:** Prevents hanging requests

**Implementation:**
```python
# Backend: advanced_features.py (Lines 731-738)
async def run_with_timeout(func, timeout: float, *args):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, *args), 
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return {"ok": False, "error": f"Timed out after {timeout}s"}
```

**How to replicate:**
- Use `asyncio.wait_for()`
- Set timeout in seconds
- Catch TimeoutError
- Return error dict

---

### ✅ 8.4 Model Lazy Loading

**What it does:** Only loads ML models when needed

**Implementation:**
```python
# Backend: advanced_features.py (Lines 236-239)
@lru_cache(maxsize=1)
def _get_ner():
    # Only loads on first call, cached thereafter
    return _safe_pipeline("ner", "dslim/bert-base-NER")
```

**How to replicate:**
- Use `@lru_cache` decorator
- Return model instance
- First call loads, subsequent calls return cached

---

### ✅ 8.5 Cross-Platform Support

**What it does:** Works on Windows, Mac, Linux

**Implementation:**
```python
# Backend: main.py (Lines 21-23)
import platform

if platform.system().lower() == "windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

**How to replicate:**
- Check platform with `platform.system()`
- Set Windows-specific event loop policy
- Use OS-independent file paths

---

## 9. Complete Feature Count

### Core Features: 12
1. Multi-input analysis (URL/Title/Article)
2. Real-time fake news detection
3. Probability scoring (Fake/Real)
4. Confidence calculation
5. Red flags detection
6. Pattern recognition
7. Article metadata extraction
8. Key entity extraction
9. Similar article finding
10. Source verification
11. Smart override logic
12. Detailed reasoning

### Advanced Features: 2
1. Text-to-Speech (TTS)
2. Named Entity Recognition (NER)

### UI Features: 10
1. Glassmorphism design
2. Animated gradient blobs
3. Dynamic probability bars
4. Color-coded verdicts
5. Loading states
6. Feature toggles
7. Responsive layout
8. Tab navigation
9. Error messages
10. Audio player

### Backend Features: 15
1. FastAPI framework
2. CORS middleware
3. Pydantic validation
4. Groq AI integration
5. Google Custom Search
6. GNews integration
7. BeautifulSoup scraping
8. HTTP range requests
9. Async operations
10. Error handling
11. Timeout handling
12. Model caching
13. Environment variables
14. JSON parsing
15. Streaming responses

---

## Total: 39 Features

---

## 10. Replication Checklist

### Backend Setup:
- [ ] Install Python 3.8+
- [ ] Create virtual environment
- [ ] Install requirements.txt
- [ ] Setup .env with API keys
- [ ] Implement FastAPI app
- [ ] Add CORS middleware
- [ ] Create Pydantic models
- [ ] Implement article extraction
- [ ] Add Google Search verification
- [ ] Integrate Groq AI
- [ ] Add GNews search
- [ ] Implement smart override logic
- [ ] Add TTS feature
- [ ] Add NER feature
- [ ] Setup audio streaming

### Frontend Setup:
- [ ] Install Node.js 18+
- [ ] Create Next.js 15 app
- [ ] Install dependencies (React, TypeScript, Tailwind)
- [ ] Create page component
- [ ] Add state management
- [ ] Implement input tabs
- [ ] Add feature toggles
- [ ] Create API integration
- [ ] Design verdict card
- [ ] Add probability bars
- [ ] Style with glassmorphism
- [ ] Add animated blobs
- [ ] Implement error handling
- [ ] Add loading states
- [ ] Create audio player
- [ ] Display NER results

---

## 11. Dependencies Quick Reference

### Backend (`requirements.txt`):
```
fastapi>=0.109.0
uvicorn>=0.27.0
python-dotenv>=1.0.0
groq>=0.4.2
beautifulsoup4>=4.12.3
lxml>=5.1.0
pydantic>=2.7.0
httpx>=0.26.0
gnews>=0.3.7
transformers>=4.36.2
torch>=2.6.0
gtts>=2.5.0
requests>=2.32.3
```

### Frontend (`package.json`):
```json
{
  "dependencies": {
    "lucide-react": "^0.556.0",
    "next": "16.0.8",
    "react": "19.2.1",
    "react-dom": "19.2.1"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "typescript": "^5",
    "tailwindcss": "^4"
  }
}
```

---

## 12. Key Files Reference

| File | Purpose | Lines | Key Features |
|------|---------|-------|--------------|
| `backend/main.py` | Core API | 856 | Article extraction, AI analysis, verification |
| `backend/advanced_features.py` | NLP features | 758 | TTS, NER, model loading |
| `backend/feature_config.py` | Configuration | 32 | Feature toggles, model settings |
| `frontend/app/page.tsx` | Main UI | 618 | Input, display, API integration |
| `frontend/app/page.module.css` | Styles | 17KB | Glassmorphism, animations |
| `frontend/app/globals.css` | Global | 1.1KB | Tailwind, utilities |

---

**This document contains every feature in your system with implementation details for exact replication!** 🎯
