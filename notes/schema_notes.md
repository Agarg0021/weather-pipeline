## Day 5 — Validation & Data Quality Findings

### Gap discovery
Initial 3 days of cron data showed only 6-11 readings/day per city 
(expected: ~24 for hourly collection). Root cause: cron only fires 
while the Mac is awake; laptop was sleeping for large portions of 
each day.

### Fix applied
Ran `sudo pmset -c sleep 0` to disable sleep while plugged into 
power, starting [DATE]. Expect denser data (closer to 24 readings/day) 
from this point forward.

### Schema change
Added `is_complete_day` flag to `daily_city_summary` — TRUE when a 
day has 18+ readings (75% of expected hourly coverage), FALSE 
otherwise. This lets downstream consumers (dashboard, further SQL) 
distinguish trustworthy daily aggregates from partial ones, rather 
than silently treating a 6-reading day the same as a 24-reading day.

### Validation performed
Manually cross-checked daily_city_summary min/max/avg against raw 
raw_readings for Delhi (Sept 6) and [other city/date] — values matched.

### Known limitation going into dashboard build
Rolling 3-day averages and day-over-day changes are currently based 
on partial days (pre-fix). These will become more reliable as fresh, 
complete days accumulate post-fix. Dashboard should note this or 
recompute closer to write-up (Day 9).
