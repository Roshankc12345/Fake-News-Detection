from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from groq import Groq
import asyncio
import platform
from gnews import GNews
import json
import re
import httpx
import requests
from bs4 import BeautifulSoup
from feature_config import get_config
from advanced_features import run_selected_features

load_dotenv()

# Ensure Windows supports asyncio subprocesses required by Playwright
if platform.system().lower() == "windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="News Detection API")

# Create audio directory if it doesn't exist
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_files")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Mount static files for audio
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class NewsRequest(BaseModel):
    content: str
    input_type: str  # "title", "url", or "article"
    enable_features: Optional[dict] = None  # e.g., {"tts": true, "ner_reality_checker": false, ...}

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
    key_entities: Optional[List[str]] = None
    article_metadata: Optional[ArticleMetadata] = None
    sources_found: Optional[List[dict]] = None
    similar_articles: Optional[List[dict]] = None
    advanced_features: Optional[dict] = None  # holds optional outputs when requested

async def extract_article_from_url(url: str) -> tuple[str, ArticleMetadata]:
    """Extract article content and metadata from URL using requests + BeautifulSoup (Playwright-free for compatibility)."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code >= 400:
            raise HTTPException(
                status_code=400,
                detail="Access denied or blocked by the source site. Please paste the full article text instead.",
            )

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove scripts/styles
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        def meta(name: str):
            tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name}) or soup.find(
                "meta", attrs={"property": f"og:{name}"}
            )
            return tag["content"] if tag and tag.has_attr("content") else None

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        title = title or meta("title") or meta("og:title") or (soup.find("h1").get_text(strip=True) if soup.find("h1") else "Unknown Title")
        author = meta("author") or meta("article:author") or (soup.find(attrs={"rel": "author"}).get_text(strip=True) if soup.find(attrs={"rel": "author"}) else None)
        author = author or (soup.find(class_=re.compile("author", re.I)).get_text(strip=True) if soup.find(class_=re.compile("author", re.I)) else "Unknown Author")
        site_name = meta("og:site_name") or meta("site_name") or requests.utils.urlparse(url).hostname

        selectors = [
            "article",
            '[role="article"]',
            ".article-content",
            ".post-content",
            ".entry-content",
            ".story-body",
            "main article",
            "main",
            ".content",
        ]
        content = ""
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(separator=" ", strip=True)
                if len(text) > 100:
                    content = text
                    break
        if not content:
            content = soup.get_text(separator=" ", strip=True)

        content = re.sub(r"\s+", " ", content).strip()
        if len(content) < 50:
            raise HTTPException(status_code=400, detail="Could not extract meaningful content from URL. Please try pasting the article text directly.")

        metadata = ArticleMetadata(
            title=title,
            source=site_name,
            url=url,
            author=author,
            summary=None  # Will be generated by AI
        )

        return content[:15000], metadata

    except Exception as e:
        error_msg = str(e)
        if isinstance(e, HTTPException):
            raise
        if "timed out" in error_msg.lower():
            raise HTTPException(status_code=400, detail="The website took too long to load. Please try pasting the article text directly instead.")
        raise HTTPException(status_code=400, detail=f"Failed to extract article: {error_msg}")

async def search_news_title(title: str) -> List[dict]:
    """Search for news articles with similar titles using GNews and optionally Google CSE"""
    try:
        google_news = GNews(language='en', max_results=5)
        results = google_news.get_news(title)

        # Optionally enrich with Google Custom Search if configured
        extra = await search_google_cse(title, max_results=4)
        merged = merge_deduplicate_results(results, extra)
        return merged
    except Exception as e:
        print(f"GNews search error: {str(e)}")
        return []

async def get_similar_articles(content: str) -> List[dict]:
    """Get similar articles based on content using GNews and optionally Google CSE"""
    try:
        # Extract key terms from content for search
        words = content.split()[:50]  # First 50 words
        search_query = ' '.join(words)
        
        google_news = GNews(language='en', max_results=4)
        results = google_news.get_news(search_query)

        # Optionally enrich with Google Custom Search if configured
        extra = await search_google_cse(search_query, max_results=4)
        merged = merge_deduplicate_results(results, extra)
        return merged[:4]  # Return top 4 merged similar articles
    except Exception as e:
        print(f"Similar articles search error: {str(e)}")
        return []

async def search_google_cse(query: str, max_results: int = 5) -> List[dict]:
    """
    Optional: Search Google Programmable Search (Custom Search Engine) if env vars are present.
    Returns a list shaped like GNews items for downstream compatibility.
    """
    api_key = os.getenv("GOOGLE_CSE_KEY")
    cx = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cx:
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": max_results}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", []) or []
            results = []
            for item in items:
                title = item.get("title")
                link = item.get("link")
                display_link = item.get("displayLink")
                if not title or not link:
                    continue
                results.append({
                    "title": title,
                    "url": link,
                    "publisher": {"title": display_link or "Unknown"}
                })
            return results
    except Exception as e:
        print(f"Google CSE search error: {str(e)}")
        return []

def merge_deduplicate_results(primary: List[dict], extra: List[dict]) -> List[dict]:
    """Merge two article lists, deduplicating by URL."""
    seen = set()
    merged = []

    def add_items(items: List[dict]):
        for itm in items or []:
            url = itm.get("url") or itm.get("link")
            if not url or url in seen:
                continue
            seen.add(url)
            merged.append(itm)

    add_items(primary)
    add_items(extra)
    return merged

async def analyze_with_groq(content: str, input_type: str, sources: Optional[List[dict]] = None) -> AnalysisResult:
    """Analyze news content using Groq's Llama 3.3 70B model"""
    
    # Prepare the prompt based on input type
    if input_type == "title":
        sources_info = ""
        if sources:
            sources_info = "\n\nRelated sources found:\n"
            for idx, source in enumerate(sources[:3], 1):
                sources_info += f"{idx}. {source.get('title', 'N/A')} - {source.get('publisher', {}).get('title', 'Unknown')}\n"
        
        prompt = f"""You are an expert fact-checker and misinformation analyst. Analyze the following news title for authenticity.

Title: "{content}"
{sources_info}

Provide a comprehensive analysis in JSON format with the following structure:
{{
    "is_fake": boolean,
    "fake_probability": float (0-100),
    "real_probability": float (0-100),
    "red_flags": [list of concerning elements],
    "patterns": [list of patterns detected],
    "reasoning": "detailed explanation of your analysis",
    "key_entities": [list of main people/organizations mentioned or implied]
}}

Consider:
1. Sensationalism and clickbait indicators
2. Source credibility (if sources found)
3. Language patterns typical of fake news
4. Emotional manipulation tactics
5. Verifiability of claims
6. Consistency with known facts

Respond ONLY with valid JSON."""

    else:  # article or url
        prompt = f"""You are an expert fact-checker and misinformation analyst. Analyze the following news article for authenticity.

Article Content:
{content[:8000]}

Provide a comprehensive analysis in JSON format with the following structure:
{{
    "is_fake": boolean,
    "fake_probability": float (0-100),
    "real_probability": float (0-100),
    "red_flags": [list of concerning elements],
    "patterns": [list of patterns detected],
    "reasoning": "detailed explanation of your analysis",
    "key_entities": [list of main people/organizations mentioned]
}}

Consider:
1. Writing quality and journalistic standards
2. Source citations and evidence
3. Bias and objectivity
4. Factual accuracy and consistency
5. Sensationalism and emotional manipulation
6. Logical fallacies and misleading information
7. Author credibility
8. Publication patterns

Respond ONLY with valid JSON."""

    try:
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional fact-checker and misinformation analyst. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        print(f"AI Response: {response_text[:500]}")  # Debug logging
        
        # Extract JSON from response - handle markdown code blocks
        if "```json" in response_text:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        elif "```" in response_text:
            json_match = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        else:
            # Try to find JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()
        
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {str(e)}")
            print(f"Attempted to parse: {response_text}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to parse AI response as JSON. Response: {response_text[:200]}"
            )
        
        # Ensure probabilities sum to 100
        fake_prob = float(analysis.get("fake_probability", 50))
        real_prob = float(analysis.get("real_probability", 50))
        
        # Normalize if needed
        total = fake_prob + real_prob
        if total > 0:
            fake_prob = (fake_prob / total) * 100
            real_prob = (real_prob / total) * 100
        else:
            fake_prob = 50.0
            real_prob = 50.0
        
        # Calculate confidence score (0-100) based on how decisive the probabilities are
        confidence_score = abs(fake_prob - real_prob)
        
        # Ensure all required fields exist with defaults
        return AnalysisResult(
            is_fake=bool(analysis.get("is_fake", fake_prob > 50)),
            fake_probability=round(fake_prob, 2),
            real_probability=round(real_prob, 2),
            confidence_score=round(confidence_score, 2),
            red_flags=analysis.get("red_flags", []) if isinstance(analysis.get("red_flags"), list) else [],
            patterns=analysis.get("patterns", []) if isinstance(analysis.get("patterns"), list) else [],
            reasoning=str(analysis.get("reasoning", "Analysis completed.")),
            key_entities=analysis.get("key_entities", []) if isinstance(analysis.get("key_entities"), list) else [],
            article_metadata=None,  # Will be set in main endpoint
            sources_found=sources if input_type == "title" else None,
            similar_articles=None  # Will be set in main endpoint
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in analyze_with_groq: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "News Detection API is running"}

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_news(request: NewsRequest):
    """Main endpoint to analyze news content"""
    
    content = request.content.strip()
    input_type = request.input_type.lower()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    if input_type not in ["title", "url", "article"]:
        raise HTTPException(status_code=400, detail="Invalid input_type. Must be 'title', 'url', or 'article'")
    
    sources = None
    metadata = None
    similar_articles = None
    
    try:
        if input_type == "url":
            # Extract article from URL with metadata
            content, metadata = await extract_article_from_url(content)
            
            # Generate summary using AI
            summary_prompt = f"Summarize the following article in one concise sentence (max 150 characters):\n\n{content[:2000]}"
            summary_response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": summary_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=100,
            )
            metadata.summary = summary_response.choices[0].message.content.strip()
            
            # Get similar articles
            similar_articles = await get_similar_articles(content)
            
            input_type = "article"  # Treat as article after extraction
            
        elif input_type == "title":
            # Search for related news articles
            sources = await search_news_title(content)
        elif input_type == "article":
            # Get similar articles for pasted articles too
            similar_articles = await get_similar_articles(content)
        
        # Build fallback metadata when user pastes title or article
        if metadata is None:
            metadata = ArticleMetadata(
                title=content if input_type == "title" else content[:120] + ("..." if len(content) > 120 else ""),
                source="User provided",
                url=None,
                author="Unknown",
                summary=None
            )
        
        # Analyze with Groq
        result = await analyze_with_groq(content, input_type, sources)
        
        # Add metadata and similar articles to result
        result.article_metadata = metadata
        result.similar_articles = similar_articles

        # Run optional advanced features if requested
        if request.enable_features:
            # Merge user selection with config defaults (only truthy keys)
            selection = {k: bool(v) for k, v in request.enable_features.items()}
            adv = await run_selected_features(content, selection)
            result.advanced_features = adv
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "groq_api_configured": bool(os.getenv("GROQ_API_KEY"))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
