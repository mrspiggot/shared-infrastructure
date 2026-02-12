"""
Data4SEO Pydantic Models

Domain models for SEO data structures.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KeywordData(BaseModel):
    """Keyword research data from Data4SEO Labs."""
    
    keyword: str
    search_volume: int = Field(description="Monthly search volume")
    competition: float = Field(ge=0, le=1, description="Competition level 0-1")
    cpc: Optional[float] = Field(default=None, description="Cost per click USD")
    keyword_difficulty: Optional[int] = Field(default=None, ge=0, le=100)
    search_intent: Optional[str] = Field(default=None, description="informational, commercial, transactional, navigational")
    trend: Optional[list[int]] = Field(default=None, description="Monthly search volume trend (12 months)")
    
    class Config:
        extra = "allow"


class SERPResult(BaseModel):
    """SERP tracking result for a specific keyword."""
    
    keyword: str
    position: Optional[int] = Field(default=None, description="Ranking position (None if not in top 100)")
    url: str
    title: str
    snippet: Optional[str] = None
    serp_features: list[str] = Field(default_factory=list, description="Featured snippets, PAA, etc.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def is_ranking(self) -> bool:
        return self.position is not None and self.position <= 100
    
    @property
    def is_top_10(self) -> bool:
        return self.position is not None and self.position <= 10


class BacklinkData(BaseModel):
    """Backlink information for a URL or domain."""
    
    source_url: str
    target_url: str
    anchor_text: Optional[str] = None
    domain_rank: Optional[int] = None
    is_dofollow: bool = True
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class AILLMMention(BaseModel):
    """
    AI/LLM citation tracking.
    
    Tracks when your content is referenced by AI assistants (ChatGPT, Claude, Perplexity, etc.)
    """
    
    query: str = Field(description="The user query that triggered the mention")
    llm_model: str = Field(description="Which LLM mentioned the content")
    mentioned_url: Optional[str] = None
    mentioned_domain: str
    mention_type: str = Field(description="direct_citation, paraphrase, recommendation")
    position: Optional[int] = Field(default=None, description="Position in LLM response if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        extra = "allow"


class KeywordResearchRequest(BaseModel):
    """Request for keyword research."""
    
    keywords: list[str] = Field(min_length=1, max_length=100)
    location_code: int = Field(default=2826, description="UK=2826, US=2840")
    language_code: str = Field(default="en")


class SERPTrackingRequest(BaseModel):
    """Request to track SERP rankings."""
    
    keywords: list[str]
    target_domain: str = "lucidate.substack.com"
    location_code: int = Field(default=2826)
    language_code: str = Field(default="en")
    depth: int = Field(default=100, description="How deep to search in SERP")


class ContentAnalysisRequest(BaseModel):
    """Request for content/sentiment analysis."""
    
    url: str
    include_sentiment: bool = True
    include_keywords: bool = True
