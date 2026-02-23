# ya-metrics-mcp

![License](https://img.shields.io/github/license/mrkhachaturov/ya-metrics-mcp)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastMCP](https://img.shields.io/badge/FastMCP-2.13%2B-green)

Model Context Protocol (MCP) server for [Yandex Metrika](https://metrika.yandex.ru/) analytics. Exposes 25 analytics tools to your AI assistant — traffic, content, demographics, geographic, conversion, and e-commerce data.

## Quick Start

### 1. Get Your OAuth Token

Go to [oauth.yandex.ru/client/new](https://oauth.yandex.ru/client/new) and create an app with **Yandex.Metrika** read access. Copy the token.

### 2. Configure Your IDE

Add to your Claude Desktop / Cursor MCP configuration:

```json
{
  "mcpServers": {
    "ya-metrics": {
      "command": "uvx",
      "args": ["ya-metrics-mcp"],
      "env": {
        "YANDEX_API_KEY": "your_oauth_token"
      }
    }
  }
}
```

> **Running from source?** Use `uv run` instead:
> ```json
> {
>   "mcpServers": {
>     "ya-metrics": {
>       "command": "uv",
>       "args": ["run", "--directory", "/path/to/ya-metrics-mcp", "ya-metrics-mcp"],
>       "env": { "YANDEX_API_KEY": "your_oauth_token" }
>     }
>   }
> }
> ```

### 3. Start Using

Ask your AI assistant to:
- **"Show me visits for counter 12345678 over the last 30 days"**
- **"What are the top traffic sources for my site?"**
- **"Compare mobile vs desktop users this month"**
- **"Which articles get the most views?"**
- **"Show conversion rates for goals 1 and 2"**

## Tools

25 tools across 6 domains:

### Traffic & Sources
| Tool | Description |
|------|-------------|
| `get_account_info` | Counter metadata and configuration |
| `get_visits` | Visit statistics with date range |
| `sources_summary` | Traffic sources overview |
| `sources_search_phrases` | Top search phrases |
| `get_traffic_sources_types` | Breakdown by source type (organic, direct, referral) |
| `get_search_engines_data` | Sessions by search engine, with robot/new-user filters |
| `get_new_users_by_source` | New user acquisition by traffic source |

### Content Analytics
| Tool | Description |
|------|-------------|
| `get_content_analytics_sources` | Sources driving readers to articles |
| `get_content_analytics_categories` | Stats by content category |
| `get_content_analytics_authors` | Author performance |
| `get_content_analytics_topics` | Performance by topic |
| `get_content_analytics_articles` | Top articles by views |

### Demographics & Devices
| Tool | Description |
|------|-------------|
| `get_user_demographics` | Age, gender, device breakdown |
| `get_device_analysis` | Browser and OS analysis |
| `get_mobile_vs_desktop` | Mobile vs desktop comparison |
| `get_page_depth_analysis` | Sessions by page depth |

### Geographic
| Tool | Description |
|------|-------------|
| `get_regional_data` | Traffic by city |
| `get_geographical_organic_traffic` | Organic traffic by country and city |

### Performance & Conversion
| Tool | Description |
|------|-------------|
| `get_page_performance` | Bounce rate and duration by URL |
| `get_goals_conversion` | Conversion rates for specified goals |
| `get_organic_search_performance` | SEO performance by query and engine |
| `get_conversion_rate_by_source_and_landing` | Conversion by source × landing page |

### Advanced
| Tool | Description |
|------|-------------|
| `get_ecommerce_performance` | E-commerce revenue by category and region |
| `get_data_by_time` | Time-series data with custom grouping |
| `get_yandex_direct_experiment` | A/B experiment bounce rates |
| `get_browsers_report` | Browser usage report |

## Configuration

All configuration via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `YANDEX_API_KEY` | ✓ | — | Yandex OAuth token |
| `YANDEX_TIMEOUT` | | `30` | Request timeout in seconds |
| `YANDEX_RETRIES` | | `3` | Retry attempts for 5xx errors |
| `YANDEX_RETRY_DELAY` | | `1.0` | Base delay between retries (seconds) |
| `READ_ONLY_MODE` | | `false` | Restrict to read-only tools |
| `ENABLED_TOOLS` | | all | Comma-separated list of allowed tools |

Copy `.env.example` to `.env` and fill in your values.

## CLI

```bash
# stdio (default, for MCP clients)
ya-metrics-mcp

# HTTP transport
ya-metrics-mcp --transport streamable-http --port 8000

# With verbose logging
ya-metrics-mcp -vv

# Load custom .env file
ya-metrics-mcp --env-file /path/to/.env
```

## Installation

**From PyPI** (once published):
```bash
uvx ya-metrics-mcp
```

**From source:**
```bash
git clone https://github.com/mrkhachaturov/ya-metrics-mcp
cd ya-metrics-mcp
uv sync
uv run ya-metrics-mcp
```

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check src/
```

## License

MIT
