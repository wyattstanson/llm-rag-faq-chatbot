import requests
from datetime import datetime, timedelta
from config.settings import NEWS_API_KEY, ALPHA_VANTAGE_KEY

MOCK_NEWS = [
    {
        "title": "Fed Holds Rates Steady Amid Inflation Concerns",
        "description": "The Federal Reserve kept interest rates unchanged as policymakers monitor inflation trends and labor market conditions.",
        "url": "https://www.reuters.com/business/finance/",
        "source": {"name": "Reuters"},
        "publishedAt": datetime.now().isoformat(),
        "category": "monetary_policy"
    },
    {
        "title": "S&P 500 Hits Record High on Tech Earnings Beat",
        "description": "Major technology companies reported stronger-than-expected earnings, propelling the S&P 500 to new record levels.",
        "url": "https://www.bloomberg.com/markets/",
        "source": {"name": "Bloomberg"},
        "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat(),
        "category": "markets"
    },
    {
        "title": "Bitcoin Surpasses $70,000 as Institutional Demand Grows",
        "description": "Cryptocurrency markets rallied as major institutional investors increased their Bitcoin holdings through spot ETFs.",
        "url": "https://coindesk.com/",
        "source": {"name": "CoinDesk"},
        "publishedAt": (datetime.now() - timedelta(hours=4)).isoformat(),
        "category": "crypto"
    },
    {
        "title": "Oil Prices Drop on Demand Concerns from China",
        "description": "Crude oil futures fell as economic data from China raised concerns about slowing energy demand in the world's largest importer.",
        "url": "https://www.ft.com/markets",
        "source": {"name": "Financial Times"},
        "publishedAt": (datetime.now() - timedelta(hours=6)).isoformat(),
        "category": "commodities"
    },
    {
        "title": "India GDP Growth Outpaces Global Forecasts",
        "description": "India's economy expanded at a rate exceeding analyst projections, cementing its position as the fastest-growing major economy.",
        "url": "https://economictimes.indiatimes.com/",
        "source": {"name": "Economic Times"},
        "publishedAt": (datetime.now() - timedelta(hours=8)).isoformat(),
        "category": "economy"
    },
    {
        "title": "Warren Buffett Increases Cash Reserves at Berkshire Hathaway",
        "description": "Berkshire Hathaway's cash pile reached a record high as Buffett continues to find limited attractive investment opportunities.",
        "url": "https://www.cnbc.com/warren-buffett/",
        "source": {"name": "CNBC"},
        "publishedAt": (datetime.now() - timedelta(hours=10)).isoformat(),
        "category": "investing"
    },
    {
        "title": "RBI Maintains Repo Rate, Eyes Inflation Trajectory",
        "description": "The Reserve Bank of India kept its benchmark rate unchanged while signaling readiness to act if inflation pressures persist.",
        "url": "https://economictimes.indiatimes.com/markets/",
        "source": {"name": "Economic Times"},
        "publishedAt": (datetime.now() - timedelta(hours=12)).isoformat(),
        "category": "monetary_policy"
    },
    {
        "title": "Nvidia Reports Record Revenue Driven by AI Chip Demand",
        "description": "Nvidia's quarterly results surpassed all forecasts as data center customers continue to rush purchases of AI accelerator chips.",
        "url": "https://www.wsj.com/tech/",
        "source": {"name": "Wall Street Journal"},
        "publishedAt": (datetime.now() - timedelta(hours=14)).isoformat(),
        "category": "markets"
    },
]

MOCK_MARKET_DATA = {
    "indices": [
        {"name": "S&P 500", "value": 5234.18, "change": 0.84, "symbol": "SPX"},
        {"name": "NASDAQ", "value": 16421.45, "change": 1.23, "symbol": "COMP"},
        {"name": "Dow Jones", "value": 38671.82, "change": -0.12, "symbol": "DJI"},
        {"name": "Nifty 50", "value": 22402.30, "change": 0.45, "symbol": "NIFTY"},
        {"name": "Sensex", "value": 73667.96, "change": 0.38, "symbol": "SENSEX"},
    ],
    "crypto": [
        {"name": "Bitcoin", "value": 71240.50, "change": 2.34, "symbol": "BTC"},
        {"name": "Ethereum", "value": 3821.20, "change": 1.87, "symbol": "ETH"},
        {"name": "Solana", "value": 182.40, "change": -0.92, "symbol": "SOL"},
    ],
    "commodities": [
        {"name": "Gold", "value": 2341.80, "change": 0.21, "symbol": "XAU"},
        {"name": "Silver", "value": 27.84, "change": -0.43, "symbol": "XAG"},
        {"name": "Crude Oil", "value": 82.15, "change": -1.12, "symbol": "WTI"},
    ],
    "forex": [
        {"name": "USD/INR", "value": 83.42, "change": 0.08, "symbol": "USDINR"},
        {"name": "EUR/USD", "value": 1.0842, "change": -0.15, "symbol": "EURUSD"},
        {"name": "GBP/USD", "value": 1.2651, "change": 0.23, "symbol": "GBPUSD"},
    ]
}

SECTOR_PERFORMANCE = [
    {"sector": "Technology", "change": 1.82},
    {"sector": "Healthcare", "change": 0.43},
    {"sector": "Financials", "change": -0.21},
    {"sector": "Energy", "change": -0.87},
    {"sector": "Consumer Disc.", "change": 0.95},
    {"sector": "Industrials", "change": 0.34},
    {"sector": "Materials", "change": -0.52},
    {"sector": "Utilities", "change": 0.17},
    {"sector": "Real Estate", "change": -0.63},
    {"sector": "Comm. Services", "change": 1.24},
]


def fetch_news(page_size=12):
    if not NEWS_API_KEY:
        return MOCK_NEWS[:page_size]
    try:
        url = (
            f"https://newsapi.org/v2/everything"
            f"?q=finance+stock+market+economy+investing"
            f"&sortBy=publishedAt&pageSize={page_size}&apiKey={NEWS_API_KEY}"
        )
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
    except Exception:
        pass
    return MOCK_NEWS[:page_size]


def fetch_market_data():
    return MOCK_MARKET_DATA


def fetch_sector_performance():
    return SECTOR_PERFORMANCE


def fetch_fear_greed():
    return 62


def fetch_sparkline_data():
    import math
    import random
    base = 5000
    return [round(base + math.sin(i * 0.3) * 80 + random.uniform(-20, 20), 2) for i in range(30)]