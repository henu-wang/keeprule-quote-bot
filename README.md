# KeepRule Quote Bot

Auto-publish investing quotes from legendary investors to grow your audience and drive traffic to [keeprule.com](https://keeprule.com).

## Features

- 365 curated investing quotes from Buffett, Munger, Graham, Lynch, Dalio, Fisher, Howard Marks, Soros, Templeton, and more
- Multi-platform support: Bluesky, Telegram, Twitter/X
- 4 post templates: quote only, with context, with discussion question, thread
- Automatic deduplication - cycles through all quotes before repeating
- Dry-run mode for previewing posts
- Statistics tracking
- Cron-ready for fully automated scheduling

## Quick Start

```bash
# Install dependencies
pip install requests python-dotenv

# Optional: for Twitter support
pip install tweepy

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

# Preview a post (no publishing)
python bot.py --dry-run --platform bluesky

# Publish to Bluesky
python bot.py --platform bluesky

# Publish to all platforms
python bot.py --platform all

# Use a specific template
python bot.py --platform bluesky --template quote_with_question

# Post a thread
python bot.py --platform bluesky --template thread

# View statistics
python bot.py --list-stats
```

## Configuration

Create a `.env` file with your credentials:

```env
# Bluesky
BLUESKY_HANDLE=yourname.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHANNEL_ID=@yourchannel

# Twitter/X
TWITTER_API_KEY=xxxxx
TWITTER_API_SECRET=xxxxx
TWITTER_ACCESS_TOKEN=xxxxx
TWITTER_ACCESS_SECRET=xxxxx
```

## Automated Scheduling (Cron)

```bash
# Weekday posts at 9 AM and 5 PM ET
0 13 * * 1-5 cd /path/to/keeprule-quote-bot && python3 bot.py --platform all --template quote_only >> /tmp/quote-bot.log 2>&1
0 21 * * 1-5 cd /path/to/keeprule-quote-bot && python3 bot.py --platform all --template quote_with_question >> /tmp/quote-bot.log 2>&1

# Weekend post at 10 AM ET
0 14 * * 0,6 cd /path/to/keeprule-quote-bot && python3 bot.py --platform all --template quote_with_context >> /tmp/quote-bot.log 2>&1
```

See [schedule.md](schedule.md) for the full publishing strategy.

## Quote Distribution

| Author | Count |
|--------|-------|
| Warren Buffett | 100 |
| Charlie Munger | 60 |
| Benjamin Graham | 40 |
| Peter Lynch | 30 |
| Ray Dalio | 30 |
| Philip Fisher | 25 |
| Howard Marks | 25 |
| George Soros | 15 |
| John Templeton | 15 |
| Other masters | 25 |

## Templates

| Template | Use case |
|----------|----------|
| `quote_only` | Clean, minimal format. Best for daily posts. |
| `quote_with_context` | Adds background story. Good for weekends. |
| `quote_with_question` | Drives engagement with a discussion prompt. |
| `thread` | 3-part thread for deeper content. Best on Thursdays. |

## Files

```
keeprule-quote-bot/
├── bot.py              # Main bot script
├── quotes.json         # 365 investing quotes
├── posted.json         # Auto-generated: tracks posted quotes
├── templates/          # Post format templates
│   ├── template_quote_only.txt
│   ├── template_quote_with_context.txt
│   ├── template_quote_with_question.txt
│   └── template_thread.txt
├── schedule.md         # Publishing strategy & cron config
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## License

MIT

## 🔗 More KeepRule Resources

### Free Tools
- [Investor Personality Quiz](https://henu-wang.github.io/investor-personality-quiz/) - Which legendary investor are you?
- [Investment Scorecard](https://henu-wang.github.io/keeprule-investment-scorecard/) - Rate any stock like Buffett
- [Portfolio Health Check](https://henu-wang.github.io/keeprule-tools/portfolio-check.html) - Grade your portfolio
- [Fear & Greed Calculator](https://henu-wang.github.io/keeprule-tools/fear-greed.html) - Market sentiment tool
- [Decision Tree](https://henu-wang.github.io/keeprule-tools/decision-tree.html) - Buy/Hold/Sell guidance
- [30-Day Challenge](https://henu-wang.github.io/keeprule-challenge/) - Transform your investing

### For Developers
- [Free API](https://henu-wang.github.io/keeprule-api/) - 100 principles, 20 authors
- [NPM Package](https://github.com/henu-wang/keeprule-npm) - `npm install keeprule`
- [PyPI Package](https://github.com/henu-wang/keeprule-pypi) - `pip install keeprule`
- [Chrome Extension](https://github.com/henu-wang/keeprule-chrome-extension)
- [Discord Bot](https://github.com/henu-wang/keeprule-discord-bot)
- [Embeddable Widget](https://github.com/henu-wang/keeprule-widget)

### Learning
- [Master Guides](https://henu-wang.github.io/keeprule-masters/) - Buffett, Munger, Graham & more
- [Free Ebook](https://henu-wang.github.io/keeprule-ebook/download.html) - 100 Investment Principles
- [Email Course](https://henu-wang.github.io/keeprule-email-course/) - 7-day Buffett course
- [Infographics](https://henu-wang.github.io/keeprule-infographics/) - Visual investing guides

---
Built by [William Wang](https://keeprule.com) | [All Tools](https://henu-wang.github.io/keeprule-hub/)
