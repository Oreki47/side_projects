import googlemaps
import pandas as pd

from config.py import target1, target2, sources, api_key
from datetime import datetime

gmaps = googlemaps.Client(key=api_key)

now = datetime.now()
results = [now.strftime("%Y-%m-%d %H:%M:%S")]
for source in sources:
    result = gmaps.directions(
      source,
      target1,
      mode="driving",
      departure_time=now,
      )
    results.append(result[0]['legs'][0]['duration_in_traffic']['value'] // 60)

result = gmaps.directions(
  target1,
  target2,
  mode="driving",
  departure_time=now,
  )
results.append(result[0]['legs'][0]['duration_in_traffic']['value'] // 60)

    
if now.weekday() in [5, 6] and now.hour in [x for x in range(12, 18)]:
    df = pd.read_csv('I:\OneDrive\Github\Python\Others\Traffic_Monitoring\log.csv')
    tp = pd.DataFrame([results], columns=df.columns)
    df = df.append(tp)
    df.to_csv('log.csv', index=False)

# 