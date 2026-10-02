import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

OUTPUT = "news.json"

FEEDS = [
    ("Presse internationale", "https://news.google.com/rss/search?q=competition+law+antitrust&hl=en-US&gl=US&ceid=US:en"),
    ("France", "https://news.google.com/rss/search?q=droit+concurrence+antitrust+France&hl=fr&gl=FR&ceid=FR:fr"),
    ("Maroc", "https://news.google.com/rss/search?q=concurrence+antitrust+Maroc&hl=fr&gl=MA&ceid=MA:fr"),
    ("Europe", "https://news.google.com/rss/search?q=EU+antitrust+competition+merger&hl=en&gl=GB&ceid=GB:en"),
    ("FTC", "https://www.ftc.gov/feeds/press-release-competition.xml"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 My-Performance-NewsBot/1.0"
}


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def parse_feed(xml_data, category):
    root = ET.fromstring(xml_data)
    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        description = clean_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "").strip()

        source = item.findtext("source", "").strip()

        if not source:
            source = category

        if not title or not link:
            continue

        items.append({
            "title": title,
            "url": link,
            "description": description[:300],
            "date": pub_date,
            "source": source,
            "category": category
        })

    return items


def main():
    all_items = []
    seen_titles = set()

    for category, feed_url in FEEDS:
        try:
            data = fetch(feed_url)
            items = parse_feed(data, category)

            for item in items:
                key = item["title"].lower()

                if key in seen_titles:
                    continue

                seen_titles.add(key)
                all_items.append(item)

        except Exception as error:
            print(f"Erreur pour {category}: {error}")

    all_items = all_items[:60]

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": all_items
    }

    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print(f"{len(all_items)} articles enregistrés dans {OUTPUT}")


if __name__ == "__main__":
    main()
