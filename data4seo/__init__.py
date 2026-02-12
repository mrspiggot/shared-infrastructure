"""
Data4SEO Client Library

Provides SEO intelligence for Horizon article distribution and tracking.

Key capabilities:
- Keyword research (search volume, difficulty, trends)
- SERP tracking (monitor article rankings)
- AI citation monitoring (track if LLMs reference your content)
- Backlink analysis
"""

from .client import Data4SEOClient
from .models import (
    KeywordData,
    SERPResult,
    BacklinkData,
    AILLMMention,
)

__all__ = [
    "Data4SEOClient",
    "KeywordData",
    "SERPResult", 
    "BacklinkData",
    "AILLMMention",
]
