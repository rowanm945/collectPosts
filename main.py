from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

from scraper import scrape_posts

app = FastAPI(
    title="CollectPosts API",
    description="Social media scraping API for Reddit, YouTube, and Instagram",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    sources: List[str]
    query: str
    days: int = 7
    limit_per_source: int = 10

@app.get("/")
async def root():
    return {
        "message": "CollectPosts API - Social Media Scraping Service",
        "status": "running",
        "endpoints": {
            "scrape": "/scrape-multi-source (POST)",
            "health": "/health (GET)"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "collectposts"}

@app.post("/scrape-multi-source")
async def scrape_multiple_sources(request: ScrapeRequest):
    try:
        # Limit maximum posts to prevent timeouts
        max_limit = min(request.limit_per_source, 50000)
        
        # Convert days to time_passed string
        time_mapping = {1: "day", 7: "week", 30: "month", 365: "year"}
        time_passed = time_mapping.get(request.days, "week")
        
        # Use centralized scraping function
        all_posts = scrape_posts(
            sources=request.sources,
            query=request.query,
            time_passed=time_passed,
            limit=max_limit
        )
        
        # Count posts by source
        source_breakdown = {}
        for post in all_posts:
            source = post.get("source", "unknown")
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        return {
            "status": "success",
            "query": request.query,
            "sources": request.sources,
            "days": request.days,
            "total_posts": len(all_posts),
            "source_breakdown": source_breakdown,
            "all_posts": all_posts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-source scraping failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
