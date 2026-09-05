# Schema Notes — Open-Meteo

## Fields captured
- temperature_2m (°C)
- relative_humidity_2m (%)
- wind_speed_10m (km/h)
- precipitation (mm)

## Cities + coordinates (from geocoding API)
- Jaipur:    26.91962, 75.78781
- Delhi:     28.65195, 77.23149
- Mumbai:    19.07283, 72.88261
- New York:  40.71427, -74.00597
- Singapore: 1.28967, 103.85007

## Gotchas
- timezone=auto returns LOCAL time per city (confirmed: New York shows
  04:15 while Indian cities show 13:45 at the same real moment).
  Decision: store everything as UTC in the DB, convert to local only
  for display — makes cross-city SQL comparisons simple.
- "current" = single live snapshot (this is what I'll fetch on a schedule
  to build history)
- "hourly" = forecast array, not historical data — not something I store
  long-term, just useful for context/validation
- Geocoding only needs to run once per city — cache these coordinates,
  don't call the geocoding API on every scheduled fetch
