# KeepRule Quote Bot - Publishing Schedule

## Daily Schedule

| Time (UTC) | Time (US Eastern) | Time (China CST) | Purpose |
|------------|-------------------|-------------------|---------|
| 13:00 | 9:00 AM | 9:00 PM | Morning post (US market open) |
| 21:00 | 5:00 PM | 5:00 AM next day | Evening post (US market close) |

## Weekly Plan

| Day | Posts | Template Strategy |
|-----|-------|-------------------|
| Monday | 2 | quote_only + quote_with_question |
| Tuesday | 2 | quote_with_context + quote_only |
| Wednesday | 2 | quote_only + quote_with_question |
| Thursday | 3 | quote_only + thread + quote_only |
| Friday | 2 | quote_with_context + quote_only |
| Saturday | 1 | quote_with_question |
| Sunday | 1 | quote_with_context |

**Weekly total: 13 posts (~2/day average)**

## Cron Configuration

```bash
# Edit crontab: crontab -e

# Weekday morning post (9 AM ET / 1 PM UTC)
0 13 * * 1-5 cd /Users/wangkai/keeprule-quote-bot && python3 bot.py --platform all --template quote_only >> /tmp/quote-bot.log 2>&1

# Weekday evening post (5 PM ET / 9 PM UTC)
0 21 * * 1-5 cd /Users/wangkai/keeprule-quote-bot && python3 bot.py --platform all --template quote_with_question >> /tmp/quote-bot.log 2>&1

# Thursday extra thread post (12 PM ET / 4 PM UTC)
0 16 * * 4 cd /Users/wangkai/keeprule-quote-bot && python3 bot.py --platform all --template thread >> /tmp/quote-bot.log 2>&1

# Weekend single post (10 AM ET / 2 PM UTC)
0 14 * * 0,6 cd /Users/wangkai/keeprule-quote-bot && python3 bot.py --platform all --template quote_with_context >> /tmp/quote-bot.log 2>&1
```

## Special Dates Calendar

| Date | Event | Special Content |
|------|-------|-----------------|
| Aug 30 | Warren Buffett Birthday | Post top Buffett quotes all day |
| Jan 1 | Charlie Munger Birthday | Post Munger quotes |
| May (first Saturday) | Berkshire Annual Meeting | Thread on Berkshire wisdom |
| May 9 | Benjamin Graham Birthday | Graham quotes series |
| Mar 11 | Peter Lynch Day | Lynch quotes series |
| Sep 12 | Ray Dalio Birthday | Dalio principles series |
| Aug 12 | George Soros Birthday | Soros quotes |
| Nov 29 | John Templeton Birthday | Templeton quotes |
| Sep 8 | Philip Fisher Birthday | Fisher checklist quotes |
| Oct 19 | Black Monday Anniversary | Risk management quotes |
| Oct 29 | 1929 Crash Anniversary | Market cycle quotes |

## Best Engagement Practices

1. **Timing**: US market hours (9:30 AM - 4 PM ET) get highest engagement
2. **Hashtags**: Keep 3-5 per post, mix broad (#investing) with niche (#valueinvesting)
3. **Questions**: Posts with questions get 2-3x more replies
4. **Threads**: Use on Thursdays for deeper content, higher save/bookmark rates
5. **Consistency**: Same time every day builds habit in followers
6. **CTA**: Always include keeprule.com link for traffic

## Growth Targets

| Month | Goal | Strategy |
|-------|------|----------|
| Month 1 | 100 followers (Bluesky) | Daily posts, engage with investing community |
| Month 2 | 300 followers | Add question templates, start threads |
| Month 3 | 500 followers | Cross-platform presence established |
| Month 6 | 1,000 followers | Consistent brand, referral traffic to keeprule.com |
| Month 12 | 3,000+ followers | Authority in investing wisdom niche |
