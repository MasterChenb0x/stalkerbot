#!/usr/bin/env python3
"""
stalkerbot.py — X.com reconnaissance tool v2.0

Replaces: grabber.rb + stalkerbot.py + parser.sh + tweet_scrape_target.sh + tweet_resolve_ids.sh

Requirements (minimal):
    pip install requests          # mandatory
    pip install tweepy            # optional, unlocks API features

Credentials can be supplied via a JSON file with four keys:
    {
        "consumer_key": "...",
        "consumer_secret": "...",
        "access_token": "...",
        "access_token_secret": "..."
    }
Legacy 4-line TwiTokens.txt is also accepted.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import random
from pathlib import Path

# Soft imports — graceful degradation
try:
    import requests
except ImportError as exc:                     # noqa: F841
    requests = None                            # type: ignore[misc]

try:
    import tweepy
except ImportError as exc:                     # noqa: F841
    tweepy = None                              # type: ignore[misc]

DEFAULT_CRED_FILE = os.path.expanduser("~/.stalkerbot_credentials.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.0.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
}


def sleep_jitter(base: float = 5.0, jitter: float = 5.0) -> None:
    """Sleep with random jitter to stay under rate-limit radars."""
    time.sleep(base + random.uniform(0, jitter))


def load_creds(path: str) -> dict:
    """Load JSON credentials or legacy 4-line TwiTokens.txt."""
    p = Path(path)
    if not p.exists():
        return {}
    text = p.read_text()
    if text.strip().startswith("{"):
        return json.loads(text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) >= 4:
        return {
            "consumer_key": lines[0],
            "consumer_secret": lines[1],
            "access_token": lines[2],
            "access_token_secret": lines[3],
        }
    return {}


def x_url(screen_name: str, tweet_id: str = None) -> str:
    """Build an x.com URL."""
    if tweet_id:
        return f"https://x.com/{screen_name}/status/{tweet_id}"
    return f"https://x.com/{screen_name}"


class StalkerBot:
    def __init__(self, creds_path: str = None):
        self.api = None          # Tweepy API(v1.1)
        self.client = None       # Tweepy Client(v2)
        self.creds = load_creds(creds_path) if creds_path else {}
        if self.creds:
            self._init_tweepy()

    def _init_tweepy(self):
        """Wire up Tweepy API + Client when tweepy is installed and creds exist."""
        if tweepy is None:
            return
        try:
            auth = tweepy.OAuthHandler(
                self.creds["consumer_key"], self.creds["consumer_secret"]
            )
            auth.set_access_token(
                self.creds["access_token"], self.creds["access_token_secret"]
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            self.client = tweepy.Client(
                consumer_key=self.creds["consumer_key"],
                consumer_secret=self.creds["consumer_secret"],
                access_token=self.creds["access_token"],
                access_token_secret=self.creds["access_token_secret"],
                wait_on_rate_limit=True,
            )
            print("[+] Tweepy authenticated (API v1.1 + Client v2)")
        except Exception as exc:
            print(f"[!] Tweepy init failed: {exc}")

    # ------------------------------------------------------------------
    # feature: follow target's network
    # ------------------------------------------------------------------
    def follow_target_network(self, target: str, my_handle: str, dry_run: bool = False):
        """
        Follow the followers and friends of a target.  
        NOTE: X API v2 requires a Basic tier ($100/mo) for follower lookup.
              Falls back to CSV import or manual list when API access is unavailable.
        """
        if self.api is None:
            print(
                "[!] API not available. Options:\n"
                "    1. pip install tweepy\n"
                "    2. Provide credentials via --creds\n"
                "    3. X API Basic tier ($100/mo) is required for followers lookup.\n"
                "    4. Or export followers/friends via X settings → Data download."
            )
            return

        print(f"[*] Pulling network for target @{target} …")
        try:
            target_followers = list(
                tweepy.Cursor(self.api.followers_ids, screen_name=target).items()
            )
            print(f"[+] Target followers: {len(target_followers)}")
        except Exception as exc:
            print(f"[!] Could not fetch target followers: {exc}")
            target_followers = []

        try:
            target_friends = list(
                tweepy.Cursor(self.api.friends_ids, screen_name=target).items()
            )
            print(f"[+] Target friends:   {len(target_friends)}")
        except Exception as exc:
            print(f"[!] Could not fetch target friends: {exc}")
            target_friends = []

        try:
            my_friends = list(
                tweepy.Cursor(self.api.friends_ids, screen_name=my_handle).items()
            )
            print(f"[+] My friends:         {len(my_friends)}")
        except Exception as exc:
            print(f"[!] Could not fetch my friends: {exc}")
            my_friends = []

        pool = set(target_followers) | set(target_friends)
        to_follow = sorted(pool - set(my_friends))
        print(f"[*] Accounts to follow: {len(to_follow)}")

        if dry_run:
            print("    (dry-run — skipping follows)")
            return

        for uid in to_follow:
            try:
                self.api.create_friendship(user_id=uid)
                print(f"[+] Following user_id {uid}")
                sleep_jitter(8, 7)
            except Exception as exc:
                print(f"[!] Failed to follow {uid}: {exc}")

    # ------------------------------------------------------------------
    # feature: keyword search across a user's tweets
    # ------------------------------------------------------------------
    def search_tweets(self, target: str, keyword: str, count: int = 100):
        """
        Search a user's timeline for a keyword.
        Uses API when possible; falls back to guidance on manual search.
        """
        if self.api:
            print(f"[*] Searching @{target}'s timeline via API …")
            try:
                tweets = tweepy.Cursor(
                    self.api.user_timeline,
                    screen_name=target,
                    count=min(count, 200),
                    tweet_mode="extended",
                ).items(count)

                found = 0
                for tweet in tweets:
                    text = (
                        tweet.full_text
                        if hasattr(tweet, "full_text")
                        else tweet.text
                    )
                    if keyword.lower() in text.lower():
                        print()
                        print(f"[+] {x_url(target, tweet.id)}")
                        print(f"    {text[:300].replace(chr(10), ' ')}")
                        found += 1
                print(f"\n[*] Matches: {found}")
                return
            except Exception as exc:
                print(f"[!] API search failed: {exc}")

        # HTTP fallback (limited without auth cookies)
        print(
            "[!] X.com now requires authentication for most search operations.\n"
            "    Options:\n"
            "    1. Use X API with an active project\n"
            "    2. Browser automation (Playwright / Selenium)\n"
            "    3. Manual X Search URL:\n"
            f"       https://x.com/search?q=from:{target} {keyword}&src=typed_query&f=live"
        )

    # ------------------------------------------------------------------
    # feature: resolve user IDs to screen names
    # ------------------------------------------------------------------
    def resolve_ids(self, idfile: str, outfile: str = None):
        """Resolve numeric X user IDs to screen names using x.com redirects."""
        if requests is None:
            print("[!] pip install requests")
            return

        ids = [
            ln.strip()
            for ln in Path(idfile).read_text().splitlines()
            if ln.strip()
        ]
        results = []

        print(f"[*] Resolving {len(ids)} IDs via x.com …")
        for uid in ids:
            url = f"https://x.com/intent/user?user_id={uid}"
            try:
                r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
                m = re.search(r"https?://x\.com/([A-Za-z0-9_]+)", r.url)
                if m:
                    uname = m.group(1)
                else:
                    title = re.search(r"<title>([^<]+)</title>", r.text)
                    uname = title.group(1).split("(")[0].strip() if title else "?"
                print(f"[+] {uid:>19}  →  @{uname}")
                results.append((uid, uname))
                sleep_jitter(1.5, 2.5)
            except Exception as exc:
                print(f"[!] {uid} error: {exc}")

        if outfile:
            with open(outfile, "w", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["user_id", "screen_name"])
                writer.writerows(results)
            print(f"[*] Saved to {outfile}")

    # ------------------------------------------------------------------
    # feature: parse tweet IDs out of files
    # ------------------------------------------------------------------
    def parse_ids(self, directory: str):
        """Extract 15–20 digit tweet IDs from files in a directory."""
        dp = Path(directory)
        if not dp.is_dir():
            print(f"[!] Not a directory: {directory}")
            return

        for fpath in dp.iterdir():
            if not fpath.is_file() or fpath.name.endswith(".ids.txt"):
                continue
            raw = fpath.read_text(errors="replace")
            ids = re.findall(r"\b\d{15,20}\b", raw)
            if not ids:
                continue
            outpath = fpath.with_suffix(".ids.txt")
            outpath.write_text("\n".join(ids) + "\n")
            print(f"[+] {fpath.name:30} → {len(ids)} IDs → {outpath.name}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        prog="stalkerbot",
        description="X.com social reconnaissance tool v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  %(prog)s follow -t TARGET_HANDLE -m MY_HANDLE --creds creds.json
  %(prog)s search -t TARGET_HANDLE -k password
  %(prog)s resolve ids.txt -o resolved.csv
  %(prog)s parse ./raw_tweets/""",
    )
    parser.add_argument(
        "--creds",
        default=DEFAULT_CRED_FILE,
        help="Path to credentials JSON (default: ~/.stalkerbot_credentials.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without executing them",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    follow_p = sub.add_parser("follow", help="Follow target's followers & friends")
    follow_p.add_argument("-t", "--target", required=True, help="Target X handle")
    follow_p.add_argument("-m", "--me", required=True, help="Your X handle")

    search_p = sub.add_parser("search", help="Search user's tweets for keyword")
    search_p.add_argument("-t", "--target", required=True)
    search_p.add_argument("-k", "--keyword", required=True)
    search_p.add_argument("-n", "--count", type=int, default=100)

    resolve_p = sub.add_parser("resolve", help="Resolve user IDs to screen names")
    resolve_p.add_argument("idfile", help="File with one ID per line")
    resolve_p.add_argument("-o", "--output", default="resolved.csv")

    parse_p = sub.add_parser("parse", help="Extract tweet IDs from files in a directory")
    parse_p.add_argument("directory")

    args = parser.parse_args()
    bot = StalkerBot(args.creds)

    if args.command == "follow":
        bot.follow_target_network(args.target, args.me, dry_run=args.dry_run)
    elif args.command == "search":
        bot.search_tweets(args.target, args.keyword, args.count)
    elif args.command == "resolve":
        bot.resolve_ids(args.idfile, args.output)
    elif args.command == "parse":
        bot.parse_ids(args.directory)


if __name__ == "__main__":
    main()
