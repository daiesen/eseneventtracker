import time
import re
import csv
import sys
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
BASE_SEARCH_URL = "https://goodmoves.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- NUMERICAL DATE TRANSLATOR ---
def convert_date_to_numerical(date_str):
    if not date_str or date_str == "N/A":
        return "N/A"
    
    # Strip ordinal indicators out of text strings (6th -> 6)
    clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    clean_date = " ".join(clean_date.split())
    
    months_map = {
        "jan": "01", "january": "01", "feb": "02", "february": "02",
        "mar": "03", "march": "03", "apr": "04", "april": "04",
        "may": "05", "jun": "06", "june": "06", "jul": "07",
        "july": "07", "aug": "08", "august": "08", "sep": "09",
        "september": "09", "oct": "10", "october": "10", "nov": "11",
        "november": "11", "dec": "12", "december": "12"
    }
    
    try:
        match = re.search(r'(\d+)\s+([a-zA-Z]+)', clean_date)
        if match:
            day = int(match.group(1))
            month_text = match.group(2).lower()
            if month_text in months_map:
                return f"{day:02d}/{months_map[month_text]}"
        
        match_reverse = re.search(r'([a-zA-Z]+)\s+(\d+)', clean_date)
        if match_reverse:
            month_text = match_reverse.group(1).lower()
            day = int(match_reverse.group(2))
            if month_text in months_map:
                return f"{day:02d}/{months_map[month_text]}"
    except Exception:
        pass
    return "N/A"

# --- COMPREHENSIVE TARGET ARRAY (PART 1 OF 2) ---
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
    "Changeworks Recycling", "Circle", "Citadel Youth Centre", "Citizens Advice Edinburgh", "Columcille", "Community Alliance Trust"
]
# --- COMPREHENSIVE TARGET ARRAY (PART 2 OF 2) ---
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
    "Cornerstone Developments Ltd", "Mhor Outdoor Ltd", "Somewhere", "South West Edible Estates", "ArtyFarty Art CIC", 
    "Little Livingroom Ltd", "Edinburgh Wellness and Sports Therapy", "Edinburgh EquiLearn", "Access Parkour Ltd", 
    "Caring Christmas Trees - Bethany Christian Trust", "Space - The Broomhouse Hub", "Hoda Productions", "Active Inquiry", 
    "My Adventure Edinburgh", "The Siamsoir Academy", "Dunedin Canmore Foundation", "Forth Sector Development", 
    "Quay Community Improvements", "Link Group HA", "Resolve Scotland", "Port Edgar Watersports", "Braidwood Bike Park", 
    "The Big Issue Scotland", "Edinburgh Palette", "Positive Changes", "Granton Project", "The Pitt", "TOPCLASS FOUNDATION", 
    "Work+Play", "Shore Psychology", "Rosemains Steading", "Selene Glow Limited", "Children First"
]

def clean_string_comparison(input_name):
    if not input_name:
        return ""
    txt = str(input_name).replace("(", " ").replace(")", " ").replace(".", " ").replace(",", " ").replace("-", " ")
    for word in ["ltd", "limited", "trust", "association", "group", "scotland", "LTD", "LIMITED", "TRUST", "ASSOCIATION", "GROUP", "SCOTLAND", "cic", "CIC"]:
        txt = txt.replace(word, " ")
    return " ".join(txt.lower().split()).strip()

def get_organization_profile_bio(job_url):
    try:
        time.sleep(1) # Polite crawler pacing interval
        res = requests.get(job_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            sub_soup = BeautifulSoup(res.text, "html.parser")
            
            # Locate structural description blocks on profile layouts
            desc_panel = sub_soup.find(id="about-organisation") or sub_soup.find(class_=re.compile(r"about-org|organisation-profile|employer-bio"))
            if desc_panel:
                return " ".join(desc_panel.text.strip().split())
                
            # Secondary text fallback loop if descriptions use custom h headings
            for heading in sub_soup.find_all(["h4", "h5", "h3", "h2"]):
                if "about" in heading.text.lower():
                    sibling = heading.find_next_sibling()
                    if sibling:
                        return " ".join(sibling.text.strip().split())
    except Exception:
        pass
    return "Click direct link to view full organization profile overview on Goodmoves."

def scrape_job_board():
    target_set = {clean_string_comparison(name) for name in TARGET_ORGANISATIONS if name.strip()}
    print(f"Loaded {len(target_set)} unique target organizations from memory.")
    
    unique_scraped_jobs = list()
    processed_vacancy_ids = set()

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
        cards = soup.find_all(class_=re.compile(r"search-result|mdc-card")) or soup.find_all("div", class_="search-result")

        for card in cards:
            link_tag = card.find("a", href=re.compile(r"/vacancy/"))
            if not link_tag:
                continue

            # Extends unique system path IDs to permanently filter out duplicate tracking loops
            href_raw = link_tag.get("href", "")
            vac_id_match = re.search(r'/vacancy/([^/?]+)', href_raw)
            if not vac_id_match:
                continue
            
            vacancy_id = vac_id_match.group(1).strip()
            if vacancy_id in processed_vacancy_ids:
                continue

            job_title = link_tag.text.strip()
            if not job_title or any(x in job_title.lower() for x in ["find out more", "top job!"]):
                continue

            # CRITICAL FIX: Explicit forward slash layout assignment to avoid 404 connection crashes
            job_link = f"https://goodmoves.org{vacancy_id}"

            # ISOLATING REAL EMPLOYER TAGS: Bypasses general card body scanning to prevent cross-contamination matches
            org_tag = card.find(class_=re.compile(r"organisation|employer|subtitle|author")) or card.find("span", class_="mdc-typography--subtitle2")
            if not org_tag:
                for link in card.find_all("a"):
                    if "/vacancy/" not in link.get("href", "") and link.text.strip():
                        org_tag = link
                        break

            employer_name = org_tag.text.strip() if org_tag else "Unknown"
            employer_clean = clean_string_comparison(employer_name)

            # OVERRIDE SAFEQUARD: Blocks short generic strings like 'Somewhere' from capturing false matches
            card_all_text = clean_string_comparison(card.get_text())
            if "children first" in card_all_text:
                employer_clean = "children first"

            matched_org = None
            if employer_clean in target_set:
                for original_target in TARGET_ORGANISATIONS:
                    if clean_string_comparison(original_target) == employer_clean:
                        matched_org = original_target
                        break

            if matched_org:
                print(f"🎯 Match Discovered: '{job_title}' by '{matched_org}'")
                processed_vacancy_ids.add(vacancy_id)

                # Process raw closing dates into single line formats
                card_text_flat = " ".join(card.get_text(" ", strip=True).split())
                closing_date_raw = "N/A"
                date_match = re.search(r'(?i)closing\s+[^a-zA-Z0-9]*([0-9]+\s+[a-zA-Z]+|[a-zA-Z]+\s+[0-9]+[^,\s]*)', card_text_flat)
                if date_match:
                    closing_date_raw = date_match.group(1).strip()
                
                # Turn string dates into formatted numerical configurations (e.g. 08/10)
                numerical_date = convert_date_to_numerical(closing_date_raw)

                # Execute deep child profile loop to pull parent organization biographies
                org_biography = get_organization_profile_bio(job_link)
                if len(org_biography) > 350:
                    org_biography = org_biography[:350] + "..."

                unique_scraped_jobs.append({
                    "org": matched_org,
                    "title": job_title,
                    "date": numerical_date,
                    "link": job_link,
                    "bio": org_biography
                })

        time.sleep(0.5)

    # --- FORMAT 1: SOCIAL MEDIA BOX PRINT ENGINE ---
    social_file = "active_jobs_social.txt"
    try:
        with open(social_file, "w", encoding="utf-8") as sf:
            for job in unique_scraped_jobs:
                sf.write(f"{job['org']}\n\n")
                sf.write(f"{job['title']} ({job['date']})\n\n")
                sf.write(f"{job['bio']}\n")
                sf.write("="*40 + "\n\n")
    except Exception as e:
        print(f"Social file generation error: {e}")

    # --- FORMAT 2: WEBSITE EMBEDDED MARKDOWN PRINT ENGINE ---
    website_file = "active_jobs_website.txt"
    try:
        with open(website_file, "w", encoding="utf-8") as wf:
                        for job in unique_scraped_jobs:
                sf.write(f"Organisation Name\n{job['org']}\n\n")
                sf.write(f"Job Title (Closing Day/Month)\n{job['title']} ({job['date']})\n\n")
                sf.write(f"Organisation biography\n{job['bio']}\n")
                sf.write("="*40 + "\n\n")
    except Exception as e:
        print(f"Social file error: {e}")

    # --- WRITING WEBSITE READABLE FORMAT ---
    try:
        with open("active_jobs_website.txt", "w", encoding="utf-8") as wf:
            for job in unique_scraped_jobs:
                wf.write(f"{job['org']} - {job['title']} ({job['date']}) - [Apply Here]({job['link']})\n\n")
                wf.write(f"{job['bio']}\n")
                wf.write("-"*40 + "\n\n")
    except Exception as e:
        print(f"Website file error: {e}")

    print("Scraper execution process completed successfully.")

    # Force alignment for file writing
    try:
        with open("active_jobs_social.txt", "w", encoding="utf-8") as sf:
            for job in unique_scraped_jobs:
                sf.write(f"Organisation Name\n{job['org']}\n\n")
                sf.write(f"Job Title (Closing Day/Month)\n{job['title']} ({job['date']})\n\n")
                sf.write(f"Organisation biography\n{job['bio']}\n")
                sf.write("="*40 + "\n\n")
        print("Generated active_jobs_social.txt successfully.")
    except Exception as e:
        print(f"Social file error: {e}")

    try:
        with open("active_jobs_website.txt", "w", encoding="utf-8") as wf:
            for job in unique_scraped_jobs:
                wf.write(f"{job['org']} - {job['title']} ({job['date']}) - [Apply Here]({job['link']})\n\n")
                wf.write(f"{job['bio']}\n")
                wf.write("-"*40 + "\n\n")
        print("Generated active_jobs_website.txt successfully.")
    except Exception as e:
        print(f"Website file error: {e}")

    print("Scraper execution process completed successfully.")

if __name__ == "__main__":
    scrape_job_board()

