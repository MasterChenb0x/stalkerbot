# StalkerBot

> **⚠️ Disclaimer:** This project exists to promote awareness of digital-recon capabilities. **Stalking is not ok.** Do not be a trash human being.

## What is it?

A lightweight, **single-file Python** tool for X.com (formerly Twitter) social reconnaissance.

- **Follow a target's network** — identify and follow the followers & friends of any handle
- **Search tweets by keyword** — scan a user's timeline for specific terms
- **Resolve user IDs** — turn numeric X user IDs into readable screen names
- **Parse tweet IDs from files** — extract 15–20 digit tweet IDs from messy dumps

## Requirements

| Dependency | Required | Notes |
|-----------|----------|-------|
| `python3` | ✅ Yes | 3.8+ recommended |
| `requests` | ✅ Yes | `pip install requests` |
| `tweepy`  | ❌ Optional | Enables API features (follow, search). Falls back gracefully without it. |

```bash
pip install requests tweepy
```

## Quick Start

Create a credentials JSON file (or use a legacy 4-line TwiTokens.txt):

```bash
cat > ~/.stalkerbot_credentials.json <<EOF
{
    "consumer_key": "your_consumer_key",
    "consumer_secret": "your_consumer_secret",
    "access_token": "your_access_token",
    "access_token_secret": "your_access_token_secret"
}
EOF
```

### Commands

```bash
chmod +x stalkerbot.py

# Follow target's network (requires tweepy + API access)
./stalkerbot.py follow -t TARGET_HANDLE -m MY_HANDLE --creds ~/.stalkerbot_credentials.json

# Search a user's tweets for a keyword
./stalkerbot.py search -t TARGET_HANDLE -k "secret"

# Resolve user IDs to screen names
./stalkerbot.py resolve ids.txt -o resolved.csv

# Parse tweet IDs from files in a directory
./stalkerbot.py parse ./raw_tweets/
```


## X.com Migration Notes (v2.0)

- **Upgraded** all URLs from `twitter.com` to `x.com`
- **Unified** `grabber.rb`, `stalkerbot.py`, `parser.sh`, `tweet_scrape_target.sh`, and `tweet_resolve_ids.sh` into a single Python file
- **Graceful degradation** — features work without API access (HTTP fallbacks + guidance)
- **Added** `--dry-run` flag to preview actions without executing
- **Added** CSV output for ID resolution

## X.com API Reality Check (2026)

X (formerly Twitter) now requires **paid API tiers** for most operations:

| Feature | Free Tier | Basic ($100/mo) |
|---------|-----------|-----------------|
| Write tweets | 1500/mo | 3000/mo |
| User lookup | Limited | 10,000/mo |
| Followers lookup | ❌ **Not available** | ✅ Available |

For the `follow` feature to work, you need **at least Basic tier** access and valid `consumer_key` / `consumer_secret` / `access_token` / `access_token_secret`.

## Historical Archive

| Date | Milestone |
|------|-----------|
| 2026-04-26 | v2.0 — migrated to x.com, unified codebase to Python 3 |
| 2021-07-11 | v1.2 — added Python script |
| 2015-07-28 | v1.0 — sanitized files for DC Skytalks |
