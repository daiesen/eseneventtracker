import csv
import io
import urllib.request

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQM-oJ4e-kvFBJ9sVaoZlbkduSEVuFxYUnEVxivlsOOJy_s1l9ysbuwSOf2SXpgvhlOjAqX8zF2s9ey/pub?gid=0&single=true&output=csv"


def get_organisations():
    print("Downloading organisation list from Google Sheets...")

    with urllib.request.urlopen(SHEET_URL) as response:
        csv_text = response.read().decode("utf-8")

    organisations = list(csv.DictReader(io.StringIO(csv_text)))

    print(f"Found {len(organisations)} organisations.")

    for organisation in organisations:
        print(
            f"- {organisation.get('Organisation')} "
            f"| {organisation.get('Events URL')} "
            f"| {organisation.get('Scraper Strategy')} "
            f"| Active: {organisation.get('Active')}"
        )

    return organisations


if __name__ == "__main__":
    get_organisations()
