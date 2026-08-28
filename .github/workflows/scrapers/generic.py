import json
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin


SOURCE_URL = "https://www.bridgendfarmhouse.org.uk/whats-on"


class EventParser(HTMLParser):
    def __init__(self, source_url):
        super().__init__()
        self.source_url = source_url
        self.events = []

        self.in_heading = False
        self.in_link = False
        self.in_paragraph = False

        self.current_heading = ""
        self.current_link = ""
        self.current_paragraph = ""

        self.current_event = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag in ("h1", "h2", "h3", "h4"):
            self.in_heading = True
            self.current_heading = ""

        elif tag == "a":
            self.in_link = True
            href = attrs.get("href", "")

            if href:
                self.current_link = urljoin(self.source_url, href)

        elif tag == "p":
            self.in_paragraph = True
            self.current_paragraph = ""

    def handle_data(self, data):
        text = " ".join(data.split())

        if not text:
            return

        if self.in_heading:
            self.current_heading += " " + text

        if self.in_paragraph:
            self.current_paragraph += " " + text

    def handle_endtag(self, tag):

        if tag in ("h1", "h2", "h3", "h4"):
            self.in_heading = False

            heading = self.current_heading.strip()

            if heading:
                self.current_event = {
                    "event_name": heading,
                    "event_url": "",
                    "description": "",
                    "source_url": self.source_url,
                }

        elif tag == "p":
            self.in_paragraph = False

            paragraph = self.current_paragraph.strip()

            if self.current_event and paragraph:
                self.current_event["description"] = paragraph

        elif tag == "a":
            self.in_link = False

            if self.current_event and self.current_link:
                if not self.current_event["event_url"]:
                    self.current_event["event_url"] = self.current_link

        self.current_heading = ""
        self.current_paragraph = ""


def download_page(url):
    print(f"Downloading: {url}")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def scrape_page(url):
    html = download_page(url)

    parser = EventParser(url)
    parser.feed(html)

    return parser.events


if __name__ == "__main__":
    events = scrape_page(SOURCE_URL)

    print()
    print("=" * 60)
    print(f"Found {len(events)} possible event records")
    print("=" * 60)
    print()

    for number, event in enumerate(events, start=1):
        print(f"EVENT {number}")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        print()
