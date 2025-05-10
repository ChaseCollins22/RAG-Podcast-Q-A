import feedparser, requests, json
from rich import print
from rich.pretty import Pretty
import requests
from urllib.parse import urlparse
import os

feed = feedparser.parse("https://lexfridman.com/feed/podcast/")

print(f'Number of podcasts: {len(feed.entries)}')

for episode in feed.entries:
    print(episode.title, episode.enclosures[0].href)
    mp3_url = episode.enclosures[0].href

    filename = os.path.basename(mp3_url)   
    out_path = os.path.join("data", "audio", filename)

    if os.path.exists(out_path):
        print(f'{out_path} already exists. Skipping to next file')
        continue
    
    response = requests.get(mp3_url)

    with open(out_path, "wb") as file:
      file.write(response.content)
