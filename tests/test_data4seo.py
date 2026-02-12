"""
Tests for Data4SEO client.

Note: These tests hit the real API. Use sparingly to avoid costs.
For CI, mock the HTTP calls or use recorded responses.
"""

import os
import pytest
from data4seo import Data4SEOClient, KeywordData, SERPResult


# Skip if no credentials
pytestmark = pytest.mark.skipif(
    not os.getenv("DATAFORSEO_LOGIN"),
    reason="DATAFORSEO_LOGIN not set"
)


@pytest.fixture
def client():
    return Data4SEOClient(
        login=os.getenv("DATAFORSEO_LOGIN", ""),
        password=os.getenv("DATAFORSEO_PASSWORD", ""),
    )


@pytest.mark.asyncio
async def test_get_account_balance(client: Data4SEOClient):
    """Test we can authenticate and get account info."""
    balance = await client.get_account_balance()
    assert "money" in balance or "balance" in str(balance).lower()


@pytest.mark.asyncio
async def test_keyword_research(client: Data4SEOClient):
    """Test keyword research endpoint."""
    keywords = await client.get_keyword_data(["interest rate decision"])
    
    assert len(keywords) >= 1
    assert isinstance(keywords[0], KeywordData)
    assert keywords[0].keyword == "interest rate decision"
    assert keywords[0].search_volume >= 0


@pytest.mark.asyncio
async def test_serp_tracking(client: Data4SEOClient):
    """Test SERP tracking for a known keyword."""
    result = await client.track_serp(
        keyword="bank of england",
        target_domain="bankofengland.co.uk",
        depth=10,
    )
    
    assert isinstance(result, SERPResult)
    assert result.keyword == "bank of england"
    # BoE should rank for their own name
    if result.is_ranking:
        assert result.position <= 10


@pytest.mark.asyncio  
async def test_keyword_suggestions(client: Data4SEOClient):
    """Test keyword suggestion/ideas endpoint."""
    suggestions = await client.get_keyword_suggestions(
        seed_keyword="federal reserve",
        limit=10,
    )
    
    assert len(suggestions) > 0
    assert all(isinstance(kw, KeywordData) for kw in suggestions)


# Unit tests (no API calls)

def test_serp_result_properties():
    """Test SERPResult property methods."""
    ranking = SERPResult(
        keyword="test",
        position=5,
        url="https://example.com",
        title="Test"
    )
    assert ranking.is_ranking is True
    assert ranking.is_top_10 is True
    
    not_ranking = SERPResult(
        keyword="test",
        position=None,
        url="",
        title=""
    )
    assert not_ranking.is_ranking is False
    assert not_ranking.is_top_10 is False


def test_keyword_data_model():
    """Test KeywordData validation."""
    kw = KeywordData(
        keyword="test keyword",
        search_volume=1000,
        competition=0.5,
        cpc=1.50,
        keyword_difficulty=45,
    )
    assert kw.keyword == "test keyword"
    assert kw.search_volume == 1000
    assert 0 <= kw.competition <= 1
