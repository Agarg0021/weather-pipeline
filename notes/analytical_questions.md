# Analytical Questions

1. What is the daily min/max/avg temperature per city?
2. Which city has the most volatile temperature (widest daily range)?
3. How does humidity trend across the day for each city?
4. Which city has had the most precipitation this week?
5. What's the day-over-day temperature change per city?
6. Is there a rolling 3-day average temperature trend per city?

## Answers (as of 5 sep 2026)
## Answers (as of Sept 6, 2026 — Day 3, ~10 hours of data)

1. Only partial days captured so far (data started mid-evening on 
   Sept 5). Highest average: Singapore (28.7°C on Sep 5, 27.8°C on 
   Sep 6). Lowest average: New York (24.3°C, Sep 5 only). Delhi, 
   Jaipur, and Mumbai cluster in the 24–26°C range. True daily 
   min/max (a full 24h cycle) isn't meaningful yet — each "day" here 
   only reflects a few hours, not the full day.

2. New York shows the widest range so far (4.9°C, from 21.7–26.6°C 
   on Sep 5), likely because its captured window happened to span 
   both an early-morning low and a midday peak. Other cities only 
   have a single-digit-hour window so far, so this isn't a fair 
   comparison yet — needs a full 24h cycle per city to be meaningful.

3. Clear humidity split by region: Delhi, Jaipur, and Mumbai are all 
   climbing steadily overnight (85% → 94–98%) as expected for humid, 
   post-monsoon India. New York shows the opposite pattern — dropping 
   from 74% to 44% across its captured window, consistent with a 
   drier daytime period. Singapore sits in between, rising from 
   72% to 83%. Real day-over-day comparison needs more history.

4. Mumbai leads with 1.0mm total precipitation so far, followed by 
   Delhi at 0.3mm. Singapore, New York, and Jaipur show 0.0mm in the 
   captured window. Too early to call this a real "weekly" leader — 
   this is only ~10 hours of data, not 7 days.

5. Early signal, not yet a reliable trend: every city shows a slight 
   *decrease* from Sep 5 to Sep 6 (Delhi -0.5°C, Jaipur -1.2°C, 
   Mumbai -0.4°C, Singapore -0.8°C). This is misleading right now — 
   Sep 5's "average" includes evening/night hours while Sep 6's 
   average so far is early-morning only, so the drop reflects 
   time-of-day, not a real daily trend. Will re-check once each day 
   has a full 24h window.

6. Rolling averages are technically computing (e.g., Singapore 28.7 → 
   28.2) but aren't meaningful yet since there's only 2 partial days 
   of history per city, not the full 3-day window the query is 
   designed for. This will become a real signal by Day 5.

