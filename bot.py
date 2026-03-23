#!/usr/bin/env python3
"""
KeepRule Quote Bot - Auto-publish investing quotes to multiple platforms.

Usage:
    python bot.py --platform bluesky
    python bot.py --platform telegram
    python bot.py --platform twitter
    python bot.py --platform all
    python bot.py --platform bluesky --template thread
    python bot.py --dry-run --platform bluesky
    python bot.py --list-stats

Environment variables (set in .env or export):
    BLUESKY_HANDLE      - Bluesky handle (e.g., yourname.bsky.social)
    BLUESKY_APP_PASSWORD - Bluesky app password
    TELEGRAM_BOT_TOKEN  - Telegram bot token
    TELEGRAM_CHANNEL_ID - Telegram channel ID (e.g., @yourchannel)
    TWITTER_API_KEY     - Twitter API key
    TWITTER_API_SECRET  - Twitter API secret
    TWITTER_ACCESS_TOKEN - Twitter access token
    TWITTER_ACCESS_SECRET - Twitter access token secret
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

# Optional imports - graceful degradation
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


BASE_DIR = Path(__file__).parent
QUOTES_FILE = BASE_DIR / "quotes.json"
POSTED_FILE = BASE_DIR / "posted.json"
TEMPLATES_DIR = BASE_DIR / "templates"


def load_quotes():
    """Load all quotes from quotes.json."""
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_posted():
    """Load the record of previously posted quote IDs."""
    if POSTED_FILE.exists():
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posted": [], "history": []}


def save_posted(posted_data):
    """Save the posted record to disk."""
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(posted_data, f, indent=2, ensure_ascii=False)


def pick_quote(quotes, posted_data):
    """Pick a random quote that hasn't been posted yet. Reset if all used."""
    posted_ids = set(posted_data.get("posted", []))
    all_ids = {q["id"] for q in quotes}
    available = all_ids - posted_ids

    if not available:
        print("[INFO] All 365 quotes have been posted. Resetting cycle.")
        posted_data["posted"] = []
        available = all_ids

    chosen_id = random.choice(list(available))
    quote = next(q for q in quotes if q["id"] == chosen_id)
    return quote


def load_template(template_name):
    """Load a post template from the templates directory."""
    template_file = TEMPLATES_DIR / f"template_{template_name}.txt"
    if not template_file.exists():
        print(f"[WARN] Template '{template_name}' not found, using default format.")
        return None
    with open(template_file, "r", encoding="utf-8") as f:
        return f.read()


def format_post(quote, template_name="quote_only"):
    """Format a quote into a post using the specified template."""
    template = load_template(template_name)

    hashtags_str = " ".join(quote["hashtags"])

    if template:
        post = template.replace("{{quote}}", quote["quote"])
        post = post.replace("{{author}}", quote["author"])
        post = post.replace("{{topic}}", quote["topic"])
        post = post.replace("{{hashtags}}", hashtags_str)
        post = post.replace("{{cta}}", quote["cta"])
        post = post.replace("{{url}}", "https://keeprule.com")
        return post

    # Default format
    return (
        f'"{quote["quote"]}"\n\n'
        f'-- {quote["author"]}\n\n'
        f'{hashtags_str}\n\n'
        f'{quote["cta"]}'
    )


def format_thread(quote):
    """Format a quote into a 3-post thread."""
    template = load_template("thread")
    if not template:
        # Fallback thread
        return [
            f'"{quote["quote"]}"\n\n-- {quote["author"]}',
            f'Topic: {quote["topic"]}\n\n'
            f'This principle reminds us that investing is as much about mindset '
            f'as it is about analysis. The best investors master both.',
            f'Explore more timeless investing principles from legendary investors.\n\n'
            f'{" ".join(quote["hashtags"])}\n\n'
            f'https://keeprule.com',
        ]

    parts = template.split("---THREAD_BREAK---")
    thread = []
    for part in parts:
        text = part.strip()
        text = text.replace("{{quote}}", quote["quote"])
        text = text.replace("{{author}}", quote["author"])
        text = text.replace("{{topic}}", quote["topic"])
        text = text.replace("{{hashtags}}", " ".join(quote["hashtags"]))
        text = text.replace("{{cta}}", quote["cta"])
        text = text.replace("{{url}}", "https://keeprule.com")
        thread.append(text)
    return thread


# ─── Platform Publishers ───────────────────────────────────────────────


def publish_bluesky(text):
    """Publish a post to Bluesky via AT Protocol."""
    if not HAS_REQUESTS:
        print("[ERROR] 'requests' package required. Run: pip install requests")
        return False

    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not handle or not password:
        print("[ERROR] BLUESKY_HANDLE and BLUESKY_APP_PASSWORD must be set.")
        return False

    # Create session
    session_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    session_resp = requests.post(session_url, json={
        "identifier": handle,
        "password": password,
    })

    if session_resp.status_code != 200:
        print(f"[ERROR] Bluesky auth failed: {session_resp.text}")
        return False

    session = session_resp.json()
    did = session["did"]
    access_token = session["accessJwt"]

    # Detect and create facets for links and hashtags
    facets = []
    # Find URLs
    import re
    for match in re.finditer(r'https?://[^\s]+', text):
        facets.append({
            "index": {
                "byteStart": len(text[:match.start()].encode("utf-8")),
                "byteEnd": len(text[:match.end()].encode("utf-8")),
            },
            "features": [{
                "$type": "app.bsky.richtext.facet#link",
                "uri": match.group(),
            }],
        })

    # Find hashtags
    for match in re.finditer(r'#(\w+)', text):
        facets.append({
            "index": {
                "byteStart": len(text[:match.start()].encode("utf-8")),
                "byteEnd": len(text[:match.end()].encode("utf-8")),
            },
            "features": [{
                "$type": "app.bsky.richtext.facet#tag",
                "tag": match.group(1),
            }],
        })

    # Create post
    post_url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }
    if facets:
        record["facets"] = facets

    post_resp = requests.post(post_url, json={
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": record,
    }, headers={"Authorization": f"Bearer {access_token}"})

    if post_resp.status_code == 200:
        uri = post_resp.json().get("uri", "")
        print(f"[OK] Published to Bluesky: {uri}")
        return True
    else:
        print(f"[ERROR] Bluesky post failed: {post_resp.text}")
        return False


def publish_telegram(text):
    """Publish a message to a Telegram channel."""
    if not HAS_REQUESTS:
        print("[ERROR] 'requests' package required. Run: pip install requests")
        return False

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel = os.getenv("TELEGRAM_CHANNEL_ID")

    if not token or not channel:
        print("[ERROR] TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID must be set.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": channel,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    })

    if resp.status_code == 200:
        msg_id = resp.json().get("result", {}).get("message_id", "")
        print(f"[OK] Published to Telegram: message_id={msg_id}")
        return True
    else:
        print(f"[ERROR] Telegram post failed: {resp.text}")
        return False


def publish_twitter(text):
    """Publish a tweet using Twitter API v2 (OAuth 1.0a)."""
    try:
        import tweepy
    except ImportError:
        print("[ERROR] 'tweepy' package required. Run: pip install tweepy")
        return False

    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("[ERROR] Twitter API credentials must be set.")
        return False

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )

    try:
        resp = client.create_tweet(text=text)
        tweet_id = resp.data["id"]
        print(f"[OK] Published to Twitter: https://twitter.com/i/web/status/{tweet_id}")
        return True
    except Exception as e:
        print(f"[ERROR] Twitter post failed: {e}")
        return False


PUBLISHERS = {
    "bluesky": publish_bluesky,
    "telegram": publish_telegram,
    "twitter": publish_twitter,
}


# ─── Main Logic ────────────────────────────────────────────────────────


def show_stats(quotes, posted_data):
    """Show posting statistics."""
    posted_ids = posted_data.get("posted", [])
    history = posted_data.get("history", [])

    print(f"\n{'='*50}")
    print(f"  KeepRule Quote Bot - Statistics")
    print(f"{'='*50}")
    print(f"  Total quotes:     {len(quotes)}")
    print(f"  Posted (cycle):   {len(posted_ids)}")
    print(f"  Remaining:        {len(quotes) - len(posted_ids)}")
    print(f"  Total posts ever: {len(history)}")

    # Author breakdown
    from collections import Counter
    author_counts = Counter(q["author"] for q in quotes)
    print(f"\n  Quotes by author:")
    for author, count in author_counts.most_common():
        posted_author = sum(
            1 for q in quotes
            if q["author"] == author and q["id"] in set(posted_ids)
        )
        print(f"    {author}: {posted_author}/{count}")

    if history:
        last = history[-1]
        print(f"\n  Last post: ID #{last['id']} on {last['platform']} at {last['timestamp']}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description="KeepRule Quote Bot - Auto-publish investing quotes"
    )
    parser.add_argument(
        "--platform",
        choices=["bluesky", "telegram", "twitter", "all"],
        help="Target platform (or 'all')",
    )
    parser.add_argument(
        "--template",
        choices=["quote_only", "quote_with_context", "quote_with_question", "thread"],
        default="quote_only",
        help="Post template to use (default: quote_only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the post without publishing",
    )
    parser.add_argument(
        "--list-stats",
        action="store_true",
        help="Show posting statistics",
    )
    parser.add_argument(
        "--quote-id",
        type=int,
        help="Force a specific quote ID",
    )

    args = parser.parse_args()

    quotes = load_quotes()
    posted_data = load_posted()

    if args.list_stats:
        show_stats(quotes, posted_data)
        return

    if not args.platform:
        parser.print_help()
        sys.exit(1)

    # Pick or force a quote
    if args.quote_id:
        quote = next((q for q in quotes if q["id"] == args.quote_id), None)
        if not quote:
            print(f"[ERROR] Quote ID #{args.quote_id} not found.")
            sys.exit(1)
    else:
        quote = pick_quote(quotes, posted_data)

    print(f"[INFO] Selected quote #{quote['id']} by {quote['author']}")
    print(f"[INFO] Topic: {quote['topic']}")

    # Format post
    if args.template == "thread":
        thread = format_thread(quote)
        print(f"\n--- Thread Preview ({len(thread)} posts) ---")
        for i, post in enumerate(thread, 1):
            print(f"\n[{i}/{len(thread)}]")
            print(post)
        print(f"\n--- End Preview ---\n")

        if args.dry_run:
            print("[DRY RUN] No posts published.")
            return

        # For thread, only publish first post to non-thread platforms
        text = thread[0]
    else:
        text = format_post(quote, args.template)
        print(f"\n--- Post Preview ---\n{text}\n--- End Preview ---\n")

        if args.dry_run:
            print("[DRY RUN] No posts published.")
            return

    # Publish
    platforms = list(PUBLISHERS.keys()) if args.platform == "all" else [args.platform]
    success_any = False

    for platform in platforms:
        print(f"[INFO] Publishing to {platform}...")
        publisher = PUBLISHERS[platform]
        success = publisher(text)
        if success:
            success_any = True
            posted_data["history"].append({
                "id": quote["id"],
                "platform": platform,
                "template": args.template,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    # Record the quote as posted (regardless of platform)
    if success_any:
        if quote["id"] not in posted_data["posted"]:
            posted_data["posted"].append(quote["id"])
        save_posted(posted_data)
        print(f"[OK] Done. Quote #{quote['id']} recorded as posted.")
    elif args.dry_run:
        pass
    else:
        print("[WARN] No platform succeeded.")


if __name__ == "__main__":
    main()
