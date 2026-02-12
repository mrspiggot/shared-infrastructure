"""
Data4SEO API Client

Async client for Data4SEO API with rate limiting and retry logic.

Usage:
    client = Data4SEOClient(login="email", password="api_password")
    
    # Keyword research
    keywords = await client.get_keyword_data(["fed rate decision", "fomc preview"])
    
    # SERP tracking  
    rankings = await client.track_serp("fed rate decision", target_domain="lucidate.substack.com")
    
    # AI/LLM mentions
    mentions = await client.get_llm_mentions("lucidate.substack.com")
"""

import asyncio
import base64
from datetime import datetime
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import (
    KeywordData,
    SERPResult,
    BacklinkData,
    AILLMMention,
    KeywordResearchRequest,
    SERPTrackingRequest,
)


class Data4SEOClient:
    """
    Async client for Data4SEO API.
    
    Supports:
    - DataForSEO Labs (keyword research)
    - SERP API (ranking tracking)
    - AI Optimization (LLM mention tracking)
    - Backlinks API
    """
    
    BASE_URL = "https://api.dataforseo.com/v3"
    
    def __init__(
        self,
        login: str,
        password: str,
        timeout: float = 30.0,
        max_concurrent: int = 5,
    ):
        self.login = login
        self.password = password
        self.timeout = timeout
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create auth header
        credentials = f"{login}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self._headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
    ) -> dict:
        """Make authenticated request to Data4SEO API."""
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.BASE_URL}/{endpoint}"
                
                if method.upper() == "POST":
                    response = await client.post(url, headers=self._headers, json=data)
                else:
                    response = await client.get(url, headers=self._headers)
                
                response.raise_for_status()
                return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _post(self, endpoint: str, data: list[dict]) -> dict:
        """POST with retry logic."""
        return await self._request("POST", endpoint, data)
    
    # =========================================================================
    # KEYWORD RESEARCH (DataForSEO Labs)
    # =========================================================================
    
    async def get_keyword_data(
        self,
        keywords: list[str],
        location_code: int = 2826,  # UK
        language_code: str = "en",
    ) -> list[KeywordData]:
        """
        Get keyword research data (search volume, difficulty, etc.)
        
        Cost: ~$0.01 per request + $0.0001 per keyword
        """
        payload = [{
            "keywords": keywords,
            "location_code": location_code,
            "language_code": language_code,
        }]
        
        response = await self._post("dataforseo_labs/google/bulk_keyword_difficulty/live", payload)
        
        results = []
        if response.get("tasks"):
            for task in response["tasks"]:
                if task.get("result"):
                    for item in task["result"]:
                        results.append(KeywordData(
                            keyword=item.get("keyword", ""),
                            search_volume=item.get("search_volume", 0),
                            competition=item.get("competition", 0),
                            cpc=item.get("cpc"),
                            keyword_difficulty=item.get("keyword_difficulty"),
                        ))
        
        return results
    
    async def get_keyword_suggestions(
        self,
        seed_keyword: str,
        location_code: int = 2826,
        language_code: str = "en",
        limit: int = 50,
    ) -> list[KeywordData]:
        """
        Get keyword suggestions/ideas from a seed keyword.
        
        Great for finding related article topics.
        """
        payload = [{
            "keyword": seed_keyword,
            "location_code": location_code,
            "language_code": language_code,
            "limit": limit,
        }]
        
        response = await self._post("dataforseo_labs/google/keyword_suggestions/live", payload)
        
        results = []
        if response.get("tasks"):
            for task in response["tasks"]:
                if task.get("result"):
                    for item in task["result"]:
                        if item.get("items"):
                            for kw in item["items"]:
                                results.append(KeywordData(
                                    keyword=kw.get("keyword", ""),
                                    search_volume=kw.get("keyword_info", {}).get("search_volume", 0),
                                    competition=kw.get("keyword_info", {}).get("competition", 0),
                                    cpc=kw.get("keyword_info", {}).get("cpc"),
                                    keyword_difficulty=kw.get("keyword_properties", {}).get("keyword_difficulty"),
                                    search_intent=kw.get("search_intent_info", {}).get("main_intent"),
                                ))
        
        return results
    
    # =========================================================================
    # SERP TRACKING
    # =========================================================================
    
    async def track_serp(
        self,
        keyword: str,
        target_domain: str = "lucidate.substack.com",
        location_code: int = 2826,
        language_code: str = "en",
        depth: int = 100,
    ) -> Optional[SERPResult]:
        """
        Check ranking position for a keyword.
        
        Cost: $0.002 per request
        """
        payload = [{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "depth": depth,
        }]
        
        response = await self._post("serp/google/organic/live/regular", payload)
        
        if response.get("tasks"):
            for task in response["tasks"]:
                if task.get("result"):
                    for result in task["result"]:
                        items = result.get("items", [])
                        for idx, item in enumerate(items):
                            if item.get("type") == "organic":
                                domain = item.get("domain", "")
                                if target_domain in domain:
                                    return SERPResult(
                                        keyword=keyword,
                                        position=item.get("rank_group"),
                                        url=item.get("url", ""),
                                        title=item.get("title", ""),
                                        snippet=item.get("description"),
                                        timestamp=datetime.utcnow(),
                                    )
        
        # Not ranking
        return SERPResult(
            keyword=keyword,
            position=None,
            url="",
            title="",
            snippet=None,
            timestamp=datetime.utcnow(),
        )
    
    async def batch_track_serp(
        self,
        keywords: list[str],
        target_domain: str = "lucidate.substack.com",
    ) -> list[SERPResult]:
        """Track multiple keywords in parallel."""
        tasks = [self.track_serp(kw, target_domain) for kw in keywords]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, SERPResult)]
    
    # =========================================================================
    # AI/LLM MENTION TRACKING
    # =========================================================================
    
    async def get_llm_mentions(
        self,
        domain: str,
        limit: int = 100,
    ) -> list[AILLMMention]:
        """
        Track when your domain is mentioned by AI/LLMs.
        
        This uses the AI Optimization API to see if ChatGPT, Claude, Perplexity, etc.
        are citing your content.
        
        Cost: $0.1 per request + $0.001 per result
        """
        payload = [{
            "target": domain,
            "limit": limit,
        }]
        
        response = await self._post("ai_optimization/llm_mentions/search/live", payload)
        
        results = []
        if response.get("tasks"):
            for task in response["tasks"]:
                if task.get("result"):
                    for result in task["result"]:
                        items = result.get("items", [])
                        for item in items:
                            results.append(AILLMMention(
                                query=item.get("query", ""),
                                llm_model=item.get("llm", ""),
                                mentioned_domain=domain,
                                mentioned_url=item.get("url"),
                                mention_type=item.get("mention_type", "unknown"),
                                position=item.get("position"),
                            ))
        
        return results
    
    async def check_llm_response(
        self,
        query: str,
        model: str = "gpt-4",
    ) -> dict:
        """
        Check what an LLM responds to a specific query.
        
        Useful for seeing if your content appears in AI responses.
        """
        payload = [{
            "prompt": query,
            "model": model,
        }]
        
        response = await self._post("ai_optimization/llm_responses/live", payload)
        return response
    
    # =========================================================================
    # BACKLINKS
    # =========================================================================
    
    async def get_backlinks(
        self,
        target: str,
        limit: int = 100,
    ) -> list[BacklinkData]:
        """
        Get backlinks to a URL or domain.
        
        Cost: $0.02 per request + $0.00003 per result
        """
        payload = [{
            "target": target,
            "limit": limit,
            "mode": "as_is",  # exact URL
        }]
        
        response = await self._post("backlinks/backlinks/live", payload)
        
        results = []
        if response.get("tasks"):
            for task in response["tasks"]:
                if task.get("result"):
                    for result in task["result"]:
                        items = result.get("items", [])
                        for item in items:
                            results.append(BacklinkData(
                                source_url=item.get("url_from", ""),
                                target_url=item.get("url_to", ""),
                                anchor_text=item.get("anchor"),
                                domain_rank=item.get("domain_from_rank"),
                                is_dofollow=item.get("dofollow", True),
                                first_seen=item.get("first_seen"),
                            ))
        
        return results
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    async def get_account_balance(self) -> dict:
        """Check account balance and usage."""
        response = await self._request("GET", "appendix/user_data")
        if response.get("tasks"):
            for task in response["tasks"]:
                if task.get("result"):
                    return task["result"][0]
        return {}


# Convenience function for one-off usage
async def create_client_from_env() -> Data4SEOClient:
    """Create client using environment variables."""
    import os
    
    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    
    if not login or not password:
        raise ValueError("DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD must be set")
    
    return Data4SEOClient(login=login, password=password)
