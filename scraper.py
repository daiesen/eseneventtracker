import time
import re
import csv
import sys
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION (TOTAL REWRITE - NO GOOGLE SHEETS) ---
BASE_SEARCH_URL = "https://goodmoves.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- YOUR COMPLETED 348 TARGET ORGANISATIONS ---
TARGET_ORGANISATIONS = [
    "Lauriston Farm", "Pianodrome", "The Jester", "The Likes of Us", "Afro-Glo Hair and Beauty Salon", 
    "NC: Collective", "bold - Bringing Out Leaders in Dementia", "Recalibrate Together", "Le Petit Monde Stories", 
    "The Compassion Salon", "North Merchiston Club", "Edinburgh Communities Climate Action Network", "ECCAN", 
    "Art Buds Collective", "Four Square Park Café", "Queen Margaret University Edinburgh", "Flexible Working Scotland", 
    "TrusteeConnect", "Vahanomy Ltd", "RiverRescues Animal Sanctuary", "The RIAS", "TechLink Innovations", 
    "The Royal Incorporation of Architects in Scotland", "Rosemains Steading", "Shore Psychology", "Katie Adams Coaching", 
    "The Challenges Group", "The Black Box Approach", "The Village Bistro", "Neuroinclusive Works", "Change Please", 
    "WanderWomen", "St Columba's Hospice", "Heart of Newhaven", "Data Harmonise", "Leith Comedy Festival", "RKubed", 
    "Beautify Earth", "Cou Caravaca Design", "Youdom Suya", "Boroughmuir High School", "The Pitt", "BLAST Boxing", 
    "SoberBuzz Scotland", "Passion4Social", "Welcome Brain Consulting", "Datakirk", "180 Degrees Edinburgh", 
    "Edinburgh Student Housing Co-operative", "media co-op", "Vilo Sky", "Marketing for Good", "Sanitree", 
    "Coin-Operated Press", "Social Investment Scotland", "Changeworks", "GoodCall", "Venturing Out", "Seedling", 
    "Music Broth", "Unlabelled Films", "Change Mental Health", "Abandoned Artists", "Let's Talk Young People", 
    "Universal Truth", "Dance House Scotland", "EWP", "The Edinburgh Wheels Project", "Bikes for Refugees", 
    "Edinburgh Yoga and Sports Therapy", "Rhyze Mushrooms", "Lavender Menace Queer Books Archive", "Ceilidh Crew 'n Co", 
    "Prosper Social Finance", "University of Edinburgh", "Exhibitability", "Fair Trade Co", "CADi", 
    "Edinburgh Strength Collectivel", "Homeshare Scotland", "BuildU Scotland", "Aerial Art House", "Hot Mess Productions", 
    "The Young Womens Movement", "Access Parkour", "Door in the Wall Arts Access", "Viva Life CIC", "Cultural Commons", 
    "Humanitix", "Selene Glow", "Bright Red Triangle at Napier University", "Newin", "Liminale", "Forgotten Edges", 
    "Root to Rise Freedom Foundation", "Stepping Stones North Edinburgh", "Withinsight LTD", "Seeing The Now", 
    "Transition Edinburgh South", "Beetroots Collective CIC", "Hive Mind Speaks", "The Safe Place", "In My Neighbourhood", 
    "Anne Phillips Limited", "Mhor Outdoor", "Heartsong Live", "The Ripple Project", "Cyber & Fraud Centre Scotland", 
    "Planning Aid Scotland", "The Ampersand Project", "ScotArt", "Edinburgh Community Yoga", "Street Fit Scotland", 
    "The Skelf Bike Park", "Space Artworks", "Transform Scotland", "Four Square", "St Judes Laundry", "Create Business Properties", 
    "Community Enterprise", "Space at Broomhouse Hub", "Fountainbridge Canalside Community Trust", "Black Professionals United Kingdom", 
    "Willow Den", "Into Work", "Edinburgh Open Workshop", "The Salisbury Centre", "Treasure Tree", "Queer Yoga Edinburgh", 
    "The Therapy Programme", "Corvidaeum Creative", "Edinburgh Library of Things", "Tidyscot", "Adelphe Connect", 
    "Edinburgh Printmakers", "Work+Play Hub", "Martha M Coaching", "CIEE Edinburgh: Study Abroad Charity", "Tophat Discovery", 
    "Linknet Mentoring", "Scran Academy", "The Eric Liddell Community", "Hame-ish", "Goodies", "&Parents", "PurpleByte", 
    "Shandon Publishing", "All or Nothing Aerial Dance Theatre", "Visual Literacy Matters", "Creative Arts Therapies Space", 
    "Studio Lutalica", "Communication Inclusion People", "Norton Park Business and Conference Centre", "Edinburgh Chamber of Commerce", 
    "Coorie Kitchen", "House of Jack", "The Green Team", "IntelliDigest", "Art and Spirituality", "Adhart", "ArtyFarty Art", 
    "Code Division", "Dunedin Fencing Club", "Cargo Bike Movement", "Evolution Swim School", "Edinburgh Food Social", "EcoArt", 
    "Axé Boom Boom", "Infohubme", "Hive Music Therapy", "Fathers Network Scotland", "Kin Collective", "EALA Impacts", 
    "Brave Strong Beautiful", "Bridgend Farmhouse", "People Know How", "Locavore", "little living room", "Santosa Wellness Centre", 
    "Scottish Communities Finance", "Mind Be Kind", "The Very Inclusive Play Club", "The Mindful Enterprise", "The Leith Collective", 
    "The Edinburgh Collective", "Wee Chance", "The Wee Retreat", "Spartans Community Foundation", "3Theatre", "Access Media", 
    "ACTive INquiry", "All Cleaned Up", "All Together Edinburgh", "Assist Social Capital", "Balerno Village Trust", "Bare Branding", 
    "BE United", "Best Bib n Tucker", "Bike For Good", "Blossom Wellbeing", "Bold Studio", "Breadshare", "Bro Enterprise", 
    "Caledonia Cremation", "Caledonian Foundation", "Caring Christmas Trees", "CCI Enterprises", "Coorie Catering", 
    "Changeworks Recycling", "Circle", "Citadel Youth Centre", "Citizens Advice Edinburgh", "Columcille", "Community Alliance Trust", 
    "Cornerstone", "Cre8te Opportunities Limited", "Crossing Countries", "Cyan Clayworks", "Cyrenians", "DigiTechtive Ltd", 
    "Diverse Recruitment Scotland", "Duncan Place", "Wheatley Group", "Eden Project", "Edinburgh Badminton Academy", 
    "Edinburgh Blues Club", "Edinburgh Community Food", "Edinburgh Festival of Cycling Ltd", "Edinburgh Forge CIC", 
    "Edinburgh Furniture Initiative", "Edinburgh Old Town Development Trust", "The Crannie", "Equal Exchange", 
    "Falkirk Vineyard Church (Eden Jewellery)", "Fearlessly", "Shaw Trust", "Fresh Start", "FreshSight", "Awards Plus", 
    "Geotourist", "Glasgow Centre for Inclusive Living", "Chocolates & Grace", "Grassmarket Community Project", 
    "Greyfriars Charteris Centre", "Hadeel Ltd", "Health by Science", "Heathers", "Hoda Productions Ltd", "Impact Arts", 
    "Invisible Cities", "JASS – Junior Award Scheme for Schools", "Just Festival", "Life Care – Cafe Life", 
    "Life Care – Help at Home", "Lingo Flamingo", "Link Group Ltd", "Lister Housing Co-operative Ltd", "Love Gorgie", 
    "McSence", "Media Education", "MHScot Workplace Wellbeing", "Move On Wood", "Multi-Cultural Family Base", "My Adventure", 
    "One World Shop", "Out of the Blue Arts and Educational Trust", "Pass It On", "Pilotlight", "Edinburgh Watersports", 
    "Potential in Me", "Pregnancy and Parents Centre", "Harbour", "Real Talk", "Remode Collective", "Resolve", 
    "ReUnion Canal Boats", "Rowan Alba", "Saheliya", "School for Social Entrepreneurs", "Scottish Love in Action", 
    "Scottish Storytelling Centre / The Story Cafe", "Shrub Cooperative", "Sikh Sanjog", "Silver Stag CIC", 
    "Social Enterprise Academy", "Social Print and Copy", "Social Stories Club", "Somewhere EDI", "Sports Pathway Group", 
    "T-UK Skills & Workforce Development", "Tap Into IT Where You Are", "The Big Issue", "The Bike Station", "The Bongo Club", 
    "The Crags Centre", "We Play Together", "The Edinburgh Remakery", "The Edinburgh Tool Library", "The Graphics Coop", 
    "The Melting Pot", "The Shaw Trust", "Siamsoir Irish Dance Village", "The Yard", "Think Circus", "Tiphereth Trading Ltd", 
    "Transform Creative", "Tribe Porty", "Volunteer Edinburgh", "WHALE Arts", "YOU CAN COOK", "The Young Women's Movement", 
    "Edible Estates", "Lifecare", "LocalMotive Markets", "Upmo", "Keystone Women", "Norton Park", "YWCA Scotland", "CCI", 
    "Cornerstone Developments Ltd", "Mhor Outdoor Ltd", "Somewhere", "South West Edible Estates", "ArtyFarty Art CIC", 
    "Little Livingroom Ltd", "Edinburgh Wellness and Sports Therapy", "Edinburgh EquiLearn", "Access Parkour Ltd", 
    "Caring Christmas Trees - Bethany Christian Trust", "Space - The Broomhouse Hub", "Hoda Productions", "Active Inquiry", 
    "My Adventure Edinburgh", "The Siamsoir Academy", "Dunedin Canmore Foundation", "Forth Sector Development", 
    "Quay Community Improvements", "Link Group HA", "Resolve Scotland", "Port Edgar Watersports", "Braidwood Bike Park", 
    "The Big Issue Scotland", "Edinburgh Palette", "Positive Changes", "Granton Project", "The Pitt", "TOPCLASS FOUNDATION", 
    "Work+Play", "Shore Psychology", "Rosemains Steading", "Selene Glow Limited"
]
def clean_string_comparison(input_name):
    if not input_name:
        return ""
    txt = input_name.replace("(", " ").replace(")", " ").replace(".", " ").replace(",", " ").replace("-", " ")
    for word in ["ltd", "limited", "trust", "association", "group", "scotland", "LTD", "LIMITED", "TRUST", "ASSOCIATION", "GROUP", "SCOTLAND"]:
        txt = txt.replace(word, " ")
    return " ".join(txt.lower().split()).strip()

def scrape_job_board():
    target_set = {clean_string_comparison(name) for name in TARGET_ORGANISATIONS if name.strip()}
    print(f"Loaded {len(target_set)} unique target organizations from memory.")
    print("Beginning fresh search data scan on Goodmoves...")
    
    new_rows_to_append = list()

    for page_num in range(1, 21):
        print(f"Reading Page {page_num}...")
        payload = {
            "regions": "edinburgh-lothians",
            "page": page_num,
            "sort": "newest"
        }

        try:
            response = requests.get(BASE_SEARCH_URL + "/search", headers=HEADERS, params=payload, timeout=10)
            if response.status_code != 200:
                break
        except Exception:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all(class_=re.compile(r"search-result|mdc-card")) or soup.find_all("div")

        for card in cards:
            link_tag = card.find("a", href=re.compile(r"/vacancy/"))
            if not link_tag:
                continue

            job_title = link_tag.text.strip()
            if not job_title or any(x in job_title.lower() for x in ["find out more", "top job!"]):
                continue

            href = link_tag.get("href", "")
            job_link = href if href.startswith("http") else f"https://goodmoves.org{href}"

            card_text = card.get_text(" ", strip=True)
            card_clean = clean_string_comparison(card_text)

            matched_org = None
            for original_target in TARGET_ORGANISATIONS:
                target_clean = clean_string_comparison(original_target)
                if target_clean and target_clean in card_clean:
                    matched_org = original_target
                    break

            if matched_org:
                print(f"🎯 Match Discovered: '{job_title}' by '{matched_org}'")

                closing_date = "N/A"
                date_match = re.search(r'(?i)closing\s+(\d+\w*\s+\w+|\w+\s+\d+)', card_text)
                if date_match:
                    closing_date = date_match.group(0).strip()

                org_bio = "Click link to view job details."
                snippet_div = card.find(class_=re.compile(r"snippet|description|body"))
                if snippet_div:
                    org_bio = snippet_div.text.strip()
                if len(org_bio) > 300:
                    org_bio = org_bio[:300] + "..."

                new_row = [matched_org, job_title, closing_date, job_link, org_bio]
                if new_row not in new_rows_to_append:
                    new_rows_to_append.append(new_row)

        time.sleep(1)

    # Local file execution write layer
    csv_file = "active_jobs.csv"
    try:
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Organisation Name", "Job Title", "Closing Date", "Direct Link", "Organisation Biography"])
            writer.writerows(new_rows_to_append)
        print(f"SUCCESS: Compiled {len(new_rows_to_append)} live jobs into {csv_file}")
    except Exception as e:
        print(f"Failed to generate local output file: {e}")

    print("\n" + "="*50)
    print("📋 SCRAPED DATA SUMMARY IN CSV FORMAT")
    print("="*50)
    writer = csv.writer(sys.stdout, delimiter='\t')
    writer.writerow(["Organisation Name", "Job Title", "Closing Date", "Direct Link", "Organisation Biography"])
    for job in new_rows_to_append:
        writer.writerow(job)
    print("="*50 + "\n")

if __name__ == "__main__":
    scrape_job_board()
