import time
import re
import csv
import sys
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

BASE_SEARCH_URL = "https://goodmoves.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def convert_date_to_numerical(date_str):
    if not date_str or date_str == "N/A":
        return "N/A"
    clean = date_str.lower().replace("closing", "").replace(":", "").strip()
    clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', clean)
    clean = " ".join(clean.split())
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", 
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }
    try:
        m1 = re.search(r'(\d+)\s+([a-z]+)', clean)
        if m1 and m1.group(2)[:3] in months:
            return f"{int(m1.group(1)):02d}/{months[m1.group(2)[:3]]}"
        m2 = re.search(r'([a-z]+)\s+(\d+)', clean)
        if m2 and m2.group(1)[:3] in months:
            return f"{int(m2.group(2)):02d}/{months[m2.group(1)[:3]]}"
    except Exception:
        pass
    return "N/A"

# --- TARGET ORGANISATIONS LIST (PART 1 OF 2) ---
TARGET_ORGANISATIONS = [
    "Lauriston Farm", "Pianodrome", "The Jester", "The Likes of Us", "Afro-Glo Hair and Beauty Salon", 
    "NC: Collective", "bold - Bringing Out Leaders in Dementia", "Recalibrate Together", "Le Petit Monde Stories", 
    "The Compassion Salon", "North Merchiston Club", "Edinburgh Communities Climate Action Network", "ECCAN", 
    "Art Buds Collective", "Four Square Park Café", "Queen Margaret University Edinburgh", "Flexible Working Scotland", 
    "TrusteeConnect", "Vahanomy Ltd", "RiverRescues Animal Sanctuary", "The RIAS", "The Royal Incorporation of Architects in Scotland", 
    "Rosemains Steading", "Shore Psychology", "Katie Adams Coaching", "The Challenges Group", "The Black Box Approach", 
    "The Village Bistro", "Neuroinclusive Works", "Change Please", "WanderWomen", "St Columba's Hospice", "Heart of Newhaven", 
    "Data Harmonise", "Leith Comedy Festival", "RKubed", "Beautify Earth", "Cou Caravaca Design", "Youdom Suya", 
    "Boroughmuir High School", "The Pitt", "BLAST Boxing", "SoberBuzz Scotland", "Passion4Social", "Welcome Brain Consulting", 
    "Datakirk", "180 Degrees Edinburgh", "Edinburgh Student Housing Co-operative", "media co-op", "Vilo Sky", "Marketing for Good", 
    "Sanitree", "Coin-Operated Press", "Social Investment Scotland", "Changeworks", "GoodCall", "Venturing Out", "Seedling", 
    "Music Broth", "Unlabelled Films", "Change Mental Health", "Abandoned Artists", "Let's Talk Young People", "Universal Truth", 
    "Dance House Scotland", "EWP", "The Edinburgh Wheels Project", "Bikes for Refugees", "Edinburgh Yoga and Sports Therapy", 
    "Rhyze Mushrooms", "Lavender Menace Queer Books Archive", "Ceilidh Crew 'n Co", "Prosper Social Finance", "University of Edinburgh", 
    "Exhibitability", "Fair Trade Co", "CADi", "Edinburgh Strength Collectivel", "Homeshare Scotland", "BuildU Scotland", 
    "Aerial Art House", "Hot Mess Productions", "The Young Womens Movement", "Access Parkour", "Door in the Wall Arts Access", 
    "Viva Life CIC", "Cultural Commons", "Humanitix", "Selene Glow", "Bright Red Triangle at Napier University", "Newin", 
    "Liminale", "Forgotten Edges", "Root to Rise Freedom Foundation", "Stepping Stones North Edinburgh", "Withinsight LTD", 
    "Seeing The Now", "Transition Edinburgh South", "Beetroots Collective CIC", "Hive Mind Speaks", "The Safe Place", 
    "In My Neighbourhood", "Anne Phillips Limited", "Mhor Outdoor", "Heartsong Live", "The Ripple Project", 
    "Cyber & Fraud Centre Scotland", "Planning Aid Scotland", "The Ampersand Project", "ScotArt", "Edinburgh Community Yoga", 
    "Street Fit Scotland", "The Skelf Bike Park", "Space Artworks", "Transform Scotland", "Four Square", "St Judes Laundry", 
    "Create Business Properties", "Community Enterprise", "Space at Broomhouse Hub", "Fountainbridge Canalside Community Trust", 
    "Black Professionals United Kingdom", "Willow Den", "Into Work", "Edinburgh Open Workshop", "The Salisbury Centre", 
    "Treasure Tree", "Queer Yoga Edinburgh", "The Therapy Programme", "Corvidaeum Creative", "Edinburgh Library of Things", 
    "Tidyscot", "Adelphe Connect", "Edinburgh Printmakers", "Work+Play Hub", "Martha M Coaching", "CIEE Edinburgh: Study Abroad Charity", 
    "Tophat Discovery", "Linknet Mentoring", "Scran Academy", "The Eric Liddell Community", "Hame-ish", "Goodies", "&Parents", 
    "PurpleByte", "Shandon Publishing", "All or Nothing Aerial Dance Theatre", "Visual Literacy Matters", "Creative Arts Therapies Space", 
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
    "Changeworks Recycling", "Circle", "Citadel Youth Centre", "Citizens Advice Edinburgh", "Columcille", "Community Alliance Trust"
]
# --- TARGET ORGANISATIONS LIST (PART 2 OF 2) ---
TARGET_ORGANISATIONS += [
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
    "Cornerstone Developments Ltd", "Mhor Outdoor Ltd", "South West Edible Estates", "ArtyFarty Art CIC", 
    "Little Livingroom Ltd", "Edinburgh Wellness and Sports Therapy", "Edinburgh EquiLearn", "Access Parkour Ltd", 
    "Caring Christmas Trees - Bethany Christian Trust", "Space - The Broomhouse Hub", "Hoda Productions", "Active Inquiry", 
    "My Adventure Edinburgh", "The Siamsoir Academy", "Dunedin Canmore Foundation", "Forth Sector Development", 
    "Quay Community Improvements", "Link Group HA", "Resolve Scotland", "Port Edgar Watersports", "Braidwood Bike Park", 
    "The Big Issue Scotland", "Edinburgh Palette", "Positive Changes", "Granton Project", "The Pitt", "TOPCLASS FOUNDATION", 
    "Work+Play", "Shore Psychology", "Rosemains Steading", "Selene Glow Limited", "Children First"
]

def clean_string_comparison(name):
    if not name:
        return ""
    t = str(name).replace("("," ").replace(")"," ").replace("."," ").replace(","," ").replace("-"," ")
    for w in ["ltd","limited","trust","association","group","scotland","LTD","LIMITED","TRUST","ASSOCIATION","GROUP","SCOTLAND","cic","CIC"]:
        t = t.replace(w, " ")
    return " ".join(t.lower().split()).strip()

def get_profile_bio(url):
    try:
        time.sleep(1)
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            s = BeautifulSoup(r.text, "html.parser")
            p = s.find(id="about-organisation") or s.find(class_=re.compile(r"about-org|organisation-profile|employer-bio"))
            if p:
                return " ".join(p.text.strip().split())
            for h in s.find_all(["h4", "h5", "h3", "h2"]):
                if "about" in h.text.lower() and h.find_next_sibling():
                    return " ".join(h.find_next_sibling().text.strip().split())
    except:
        pass
    return "Profile overview available on the Goodmoves vacancy portal."
def scrape_job_board():
    target_set = {clean_string_comparison(name) for name in TARGET_ORGANISATIONS if name.strip()}
    print(f"Loaded {len(target_set)} unique target organizations from memory.")
    unique_scraped_jobs = list()
    processed_vacancy_ids = set()

    for page in range(1, 21):
        print(f"Reading Page {page}...")
        payload = {"regions": "edinburgh-lothians", "page": page, "sort": "newest"}
        try:
            r = requests.get(BASE_SEARCH_URL + "/search", headers=HEADERS, params=payload, timeout=10)
            if r.status_code != 200:
                break
        except:
            break

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all(class_=re.compile(r"search-result|mdc-card")) or soup.find_all("div", class_="search-result")

        for card in cards:
            link = card.find("a", href=re.compile(r"/vacancy/"))
            if not link:
                continue
            
            raw_href = link.get("href", "").split("?")[0].strip()
            v_match = re.search(r'/vacancy/([^/\s]+)', raw_href)
            if not v_match:
                continue
            
            v_id = v_match.group(1).strip()
            if v_id in processed_vacancy_ids:
                continue

            title = link.text.strip()
            if not title or any(x in title.lower() for x in ["find out more", "top job!"]):
                continue

            job_link = f"https://goodmoves.org{v_id}"

            tag = card.find(class_=re.compile(r"organisation|employer|subtitle|author")) or card.find("span", class_="mdc-typography--subtitle2")
            if not tag:
                for l in card.find_all("a"):
                    if "/vacancy/" not in l.get("href", "") and l.text.strip():
                        tag = l
                        break
            
            emp = tag.text.strip() if tag else "Unknown"
            emp_clean = clean_string_comparison(emp)
            
            if "children first" in clean_string_comparison(card.get_text()):
                emp_clean = "children first"

            if emp_clean in target_set:
                matched = "Unknown"
                for o in TARGET_ORGANISATIONS:
                    if clean_string_comparison(o) == emp_clean:
                        matched = o
                        break
                        
                print(f"🎯 Match Discovered: '{title}' by '{matched}'")
                processed_vacancy_ids.add(v_id)

                c_date = "N/A"
                for li in card.find_all("li"):
                    if "closing" in li.text.lower():
                        c_date = li.text.strip()
                        break
                if c_date == "N/A":
                    dm = re.search(r'(?i)closing\s+[^a-z0-9]*(\d+\s+[a-z]+|[a-z]+\s+\d+)', " ".join(card.get_text(" ").split()))
                    if dm:
                        c_date = dm.group(0).strip()

                num_date = convert_date_to_numerical(c_date)
                bio = get_profile_bio(job_link)
                if len(bio) > 350:
                    bio = bio[:350] + "..."

                unique_scraped_jobs.append({
                    "org": matched, "title": title, "date": num_date, "link": job_link, "bio": bio
                })
        time.sleep(0.1)

    try:
        with open("active_jobs_social.txt", "w", encoding="utf-8") as f:
            for j in unique_scraped_jobs:
                f.write(f"Organisation Name\n{j['org']}\n\nJob Title (Closing Day/Month)\n{j['title']} ({j['date']})\n\nOrganisation biography\n{j['bio']}\n" + "="*40 + "\n\n")
    except Exception as e:
        print(f"Social file error: {e}")

    try:
        with open("active_jobs_website.txt", "w", encoding="utf-8") as f:
            for j in unique_scraped_jobs:
                f.write(f"{j['org']} - {j['title']} ({j['date']}) - <a href=\"{j['link']}\" target=\"_blank\" rel=\"noopener noreferrer\">Apply Here</a>\n\n{j['bio']}\n" + "-"*40 + "\n\n")
    except Exception as e:
        print(f"Website file error: {e}")

if __name__ == "__main__":
    scrape_job_board()
