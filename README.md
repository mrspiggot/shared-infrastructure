# Lucidate Shared Infrastructure

Shared libraries and utilities for Horizon and LuciCRM.

## Components

### Data4SEO Client

Async Python client for Data4SEO API with:

- **Keyword Research**: Search volume, difficulty, trends
- **SERP Tracking**: Monitor article rankings
- **AI Citation Monitoring**: Track LLM mentions of your content
- **Backlink Analysis**: Who's linking to your content

```python
from data4seo import Data4SEOClient

client = Data4SEOClient(
    login="richard.walker@lucidate.co.uk",
    password="your_api_password"
)

# Research keywords for an article
keywords = await client.get_keyword_data(["fed rate decision", "fomc preview"])

# Track rankings after publishing
ranking = await client.track_serp("fed rate decision", target_domain="lucidate.substack.com")

# Check if LLMs cite your content
mentions = await client.get_llm_mentions("lucidate.substack.com")
```

## Installation

```bash
# For development (editable install)
pip install -e .

# Or add to your project's dependencies
# pip install -e ../shared_infrastructure
```

## Environment Variables

```bash
DATAFORSEO_LOGIN=richard.walker@lucidate.co.uk
DATAFORSEO_PASSWORD=your_api_password
```

## Costs (Data4SEO)

| Operation | Cost |
|-----------|------|
| Keyword research | $0.01/request + $0.0001/keyword |
| SERP check | $0.002/request |
| LLM mentions | $0.1/request + $0.001/result |
| Backlinks | $0.02/request + $0.00003/result |

Budget: ~$5-10/month for moderate usage
