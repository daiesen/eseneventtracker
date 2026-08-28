import csv
import io
import urllib.request
from html.parser import HTMLParser


class EventParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.events = []

        self.current_event = None
        self.current_link = None
        self.current_text = []

        self.in_heading = False
        self.in_paragraph = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag in ("h1", "h2", "h3"):
            self.in_heading = True
            self.current_text = []

        elif tag == "p":
            self.in_paragraph = True
            self.current_text = []

        elif tag == "a" and "href" in attrs:
            self.current_link = attrs["href"]

    def handle_data(self, data):
        text = data.strip()

        if not text:
            return

        if self.in_heading or self.in_paragraph:
            self.current_text.append(text)

    def handle_endtag(self, tag):
        text = " ".join(self.current_text).strip()

        if tag in ("h1", "h2", "h3"):
            self.in_heading = False

            if text:
                self.current_event = {
                    "event_name": text,
                    "date": "",
                    "start_time": "",
                    "end_time": "",
                    "description": "",
                    "event_url": self.current_link or "",
                }

        elif tag == "p":
            self.in_paragraph = False

            if self.current_event and text:
                self.current_event["description"] = text

                self.events.append(self.current_event)
                self.current_event = None

        self.current_text = []


def scrape_page(url):
    print(f"Downloading: {url}")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request) as response:
        html = response.read().decode("utf-8")

    parser = EventParser()
    parser.feed(html)

    return parser.events


if __name__ == "__main__":
    url = "https://www.bridgendfarmhouse.org.uk/whats-on"

    events = scrape_page(url)

    print(f"\nFound {len(events)} possible events.\n")

    for event in events:
        print(event)
