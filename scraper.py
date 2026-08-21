import os
import json
import requests
import datetime
from bs4 import BeautifulSoup

# The complete list of 80 charity/community event URLs to track
URLS = {
    "Edinburgh Printmakers": "https://edinburghprintmakers.co.uk/events/",
    "Bridgend Farmhouse": "https://www.bridgendfarmhouse.org.uk/whats-on",
    "180 Degrees Consulting Edinburgh": "https://www.180dcedinburgh.com/public-upcoming-events",
    "Think Circus": "https://thinkcircus.co.uk/book/",
    "3 Theatre": "https://www.3theatre.com/weeklyclasses",
    "Access Parkour": "https://www.accessparkour.co.uk/classes-kMYv3",
    "Adelphe Connect": "https://www.adelpheconnect.co.uk/events/",
    "Aerial Art House": "https://www.aerialarthouse.com/timetable.html",
    "All or Nothing Aerial Dance": "https://www.aerialdance.co.uk/events/",
    "Art and Spirituality": "https://art-and-spirituality.cademy.io/",
    "Google Form Sign-up": "https://docs.google.com/forms/d/e/1FAIpQLSctrLiOKcYadoO3OpfkfV6t_Dl8sPRool1HUbAyI8PDd7m6qQ/viewform",
    "Beetroots Collective": "https://www.eventbrite.co.uk/o/beetroots-collective-cic-75415648863",
    "Blast Boxing Edinburgh": "https://www.blastboxingedinburgh.com/",
    "Black Professionals UK": "https://blackprofessionals.uk/events/",
    "Be United": "https://be-united.org.uk/events/",
    "Bright Red Triangle": "https://www.brightredtriangle.co.uk/events",
    "Changeworks": "https://www.changeworks.org.uk/events/",
    "Coin Operated Press": "https://www.coinoperatedpress.com/events-calendar",
    "Corvidaeum Creative": "https://www.eventbrite.co.uk/o/corvidaeum-creative-limited-120958871315",
    "Creative Arts Therapies Space (Upcoming)": "https://www.creativeartstherapiesspace.org/upcoming-events",
    "Creative Arts Therapies Space (Humanitix)": "https://events.humanitix.com/host/creative-arts-therapies-space-cic",
    "Cyan Clayworks": "https://cyanclayworks.co/cyanclayworks/short-courses/",
    "Cyber Fraud Centre Scotland": "https://cyberfraudcentre.com/event-location/scotland",
    "Cyrenians Fundraising": "https://cyrenians.scot/events/fundraising-events",
    "Dunedinfencingclub": "https://dunedinfencingclub.square.site/events-and-shop",
    "Duncan Place": "https://duncanplace.org/whats-on2/",
    "Eden Project Communities": "https://www.tickettailor.com/events/edenprojectcommunities",
    "Edinburgh Blues": "https://www.universe.com/users/edinburgh-blues-club-5VCQBS",
    "Edinburgh Chamber": "https://www.edinburghchamber.co.uk/events/",
    "Edinburgh Community Food": "https://www.edinburghcommunityfood.org.uk/Pages/Events/",
    "ECY Social Prescribing": "https://bookwhen.com/ecy-tags-social-prescribing#focus=ev-sf1u-20200921120000",
    "Edinburgh Development Film Charter": "https://edfoc.org.uk/event-board/",
    "Edinburgh Forge": "https://edinburghforge.com/events/",
    "EOTDT Activities": "https://www.eotdt.org/activities/",
    "Edinburgh Open Workshop": "https://www.edinburghopenworkshop.co.uk/news/",
    "Fountainbridge Canalside Community Trust": "https://www.eventbrite.co.uk/o/fountainbridge-canalside-community-trust-53071164743",
    "Goodies Charity": "https://www.goodiescharity.org/whats-on/",
    "Grassmarket Community Picture House": "https://www.eventbrite.co.uk/o/grassmarket-community-picture-house-14379817006",
    "Heart of Newhaven Activity": "https://www.heartofnewhaven.co.uk/activity",
    "Heart of Newhaven Events": "https://www.heartofnewhaven.co.uk/events-1",
    "Hameish Arts CIC": "https://www.tickettailor.com/events/hameishartscic",
    "Eventbrite Host 121171348315": "https://www.eventbrite.com/o/121171348315?_gl=1*ysyk40*_up*MQ..*_ga*NTkzNzA4NDE3LjE3NzkyNzU4NjE.*_ga_TQVES5V6SH*czE3NzkyNzU4NTkkbzEkZzAkdDE3NzkyNzU4NTkkajYwJGwwJGgw",
    "Into Work": "https://intowork.org.uk/events/",
    "Kin Collective": "https://kincollective.org/whats-on/",
    "Lavender Menace": "https://lavendermenace.org.uk/events",
    "LifeCare Edinburgh": "https://www.lifecare-edinburgh.org.uk/lifecare-events/",
    "MHScot Network Meetings": "https://www.mentalhealthscot.land/mhscot-network-meetings/",
    "Norton Park": "https://events.humanitix.com/host/norton-park",
    "One World Shop Blog": "https://www.oneworldshop.co.uk/blog/",
    "Shore Psychology": "https://www.shorepsychology.co.uk/whats-on/",
    "Eventbrite Host 108506659751": "https://www.eventbrite.co.uk/o/108506659751?_gl=1*174tq5y*_up*MQ..*_ga*MTM1Nzc1MjM1MC4xNzc5Mjc2ODMw*_ga_TQVES5V6SH*czE3NzkyNzY4MjkkbzEkZzAkdDE3NzkyNzY4MjkkajYwJGwwJGgw",
    "SHRUB Coop": "https://www.shrubcoop.org/shrubevents",
    "TechLink Innovations": "https://techlinkinnovations.com/events/",
    "The Bike Station": "https://www.thebikestation.org.uk/events",
    "The Bongo Club": "https://www.thebongoclub.co.uk/events-main/events-coming-up/",
    "My Edinburgh News Events": "https://myedinburgh.org/news/#events",
    "Edinburgh Tool Library": "https://events.humanitix.com/host/edinburghtoollibrary",
    "Eric Liddell Centre": "https://ericliddell.org/whats-on/",
    "The Melting Pot Nexudus": "https://themeltingpot.spaces.nexudus.com/events?&v=latest",
    "The Pitt": "https://thepitt.co.uk/events/",
    "Edinburgh Remakery": "https://www.eventbrite.co.uk/o/edinburgh-remakery-52941865943",
    "Tiphereth Calendar": "https://www.tiphereth.org.uk/events",
    "Transition Edinburgh South": "https://www.transitionedinburghsouth.org.uk/events-in-april-2026/",
    "Tribe Porty": "https://tribeporty.org/events/",
    "Upmo News": "https://www.upmo.org/news/",
    "Volunteer Edinburgh": "https://www.volunteeredinburgh.org.uk/training-and-events/",
    "WithInsight Coaching": "https://www.tickettailor.com/events/withinsightcoachingandtraining",
    "Work Plus Play Hub": "https://workplusplayhub.com/events",
    "Out of the Blue Categories": "https://www.outoftheblue.org.uk/event-categories",
    "Pilot Light": "https://www.pilotlight.org.uk/events?_gl=1*mq0gmp*_up*MQ..*_ga*MjY4OTg3OTIuMTc3OTI4MDQwOA..*_ga_CN0GJRKMSM*czE3NzkyODA0MDckbzEkZzEkdDE3NzkyODA0MTYkajUxJGwwJGgw",
    "Planning Aid Scotland": "https://www.eventbrite.co.uk/o/planning-aid-scotland-114580068081",
    "Queer Yoga Edinburgh": "https://www.eventbrite.com/o/queer-yoga-edinburgh-56031130473",
    "ReMode Collective Baluu": "https://remode-collective.live.baluu.co.uk/events",
    "Rhyze Mushrooms": "https://www.eventbrite.co.uk/o/rhyze-mushrooms-edinburgh-42549142583",
    "Rosemains Markets": "https://www.rosemains.co.uk/event-markets",
    "Sanitree Events": "https://www.sanitree.org/events-2-1",
    "Scottish Storytelling Centre": "https://scottishstorytellingcentre.online.red61.co.uk/",
    "Community Foundation Planetary Healing": "https://www.tickettailor.com/events/communityfoundationforplanetaryhealing/2173411",
    "Social Investment Scotland": "https://www.socialinvestmentscotland.com/support/upcoming-events-and-webinars/",
    "St Columba's Hospice": "https://stcolumbashospice.org.uk/events/?category=hospice-events#events-filter",
    "Sports Pathway Group": "https://www.sportspathwaygroup.com/events/",
    "Gymcatch App Provider 8024": "https://gymcatch.com/app/provider/8024/events",
    "EVOC Eventbrite": "https://www.eventbrite.co.uk/o/evoc-17285339281",
    "Tribe Porty": "https://www.eventbrite.co.uk/o/tribe-porty-8010157332",
    "Pianodrome" : "https://www.pianodrome.org/whats-on",
    "The Compassion Salon" : "https://www.compassionsalon.com/",
    "ECCAN" : "https://www.eccan.scot/events-list",
    "Art Buds Collective" : "https://bookwhen.com/artbudsclasses/e/ev-scawg-20260904140000",
    "North Merchiston Club" : "https://www.northmerchiston.co.uk/event-list",
    "North Merchiston Club" : "https://www.northmerchiston.co.uk/services-9",
    "North Merchiston Club" : "https://www.northmerchiston.co.uk/services-9-1",
    "North Merchiston Club" : "https://www.northmerchiston.co.uk/health-wellbeing",
    "The Jester" : "https://www.outsavvy.com/organiser/the-jester-fundraisers1",
    "Reclibrate Together CIC" : "https://app.ubindi.com/Mark.Smith.Recalibrate.Together.CIC",
    "Hot Messs Productions" : "https://www.eventbrite.com/o/121171348315?_gl=1*1ta4gkf*_up*MQ..*_ga*MTY5MTE1Mjk1LjE3ODczMDQyMjQ.*_ga_TQVES5V6SH*czE3ODczMDQyMjMkbzEkZzAkdDE3ODczMDQyMjMkajYwJGwwJGgw",
    "Edinburgh Strength Collective" : "http://edinburghstrength.co.uk/ssg",
    "Edinburgh Strength Collective" : "https://www.edinburghstrength.co.uk/everyday-strong",
    "Corvidaeum Creative" : "https://corvidaeumcreative.co.uk/events/",
    "Corvidaeum Creative" : "https://events.humanitix.com/host/corvidaeum-creative",
    "Rosemains Steading" : "https://www.rosemains.co.uk/event-markets",
    "Grassmarket Community Project" : "https://grassmarket.org/whats-on/",
    "Young Womens Movement" : "https://youngwomenscot.org/get-involved/events/",
    "Martha M Coaching" : "https://events.humanitix.com/host/martha-m-coaching-martha-mattos-coelho",
    "Cultural Commons" : "https://events.cultural-commons.org/",
    "Flexible Working Scotland" : "https://www.flexibleworkingscotland.co.uk/events",
    "Leith Comedy Festival" : "https://www.leithcomedyfest.com/",
    "Adelphe Connect" : "https://www.adelpheconnect.co.uk/events/",
    "Leith Theatre" : "https://www.leiththeatre.co.uk/upcoming-events",
    "Blast Boxing" : "https://www.blastboxingedinburgh.com/",
    "Welcome Brain" : "https://www.welcomebrain.com/neurodiversity-first-responder-training",
    "Remode Collective" : "https://remode-collective.live.baluu.co.uk/timetable",
    "School for Social Entrepreneurs" : "https://www.the-sse.org/learning-support/explore-all-programmes-workshops/",
    "Scot Art" : "https://www.scot-art.co.uk/whatson/exhibitions/",
    "Scot Art" : "https://www.scot-art.co.uk/whatson/workshops/",
    "Edinburgh Festival of Cycling" : "https://edfoc.org.uk/event-board/",
    "MHScot" : "https://www.mentalhealthscot.land/mhscot-network-meetings/",
    "Fathers Network Scotland" : "https://www.fathersnetwork.org.uk/events_and_training",
    "Four Square" : "https://www.foursquare.org.uk/events-and-appeals/",
    "Multi Cultural Family Base" : "https://mcfb.org.uk/events/",
    "Fresh Stat" : "https://www.freshstartweb.org.uk/get-involved/events",
    "Edinburgh Old Town Devlopment Trust" : "https://www.eotdt.org/activities/",
    "Active Inquiry" : "https://www.eventbrite.co.uk/o/3497134775?_gl=1*1k2yoif*_up*MQ..*_ga*MTYxODIzNTQxOC4xNzg3MzEzOTA5*_ga_TQVES5V6SH*czE3ODczMTM5MDgkbzEkZzAkdDE3ODczMTM5MDgkajYwJGwwJGgw",
    "Pregnancy and Parents Centre" : "https://www.pregnancyandparents.org.uk/events",
    "Black Professionals UK" : "https://blackprofessionals.uk/events/",
    "The Salisbury Centre" : "https://www.salisburycentre.org/events/month/",
    "School for Social Entrepreneurs" : "https://www.the-sse.org/learning-support/explore-all-programmes-workshops/",
    "Aerial Art House" : "https://www.aerialarthouse.com/taster-classes.html",
    "Aerial Art House" : "https://aerial-art-house.classforkids.io/",
    
    
    


}

HISTORY_FILE = "history.json"
OUTPUT_FILE = "weekly_summary.md"

def fetch_page_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip noisy elements
        for el in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            el.extract()
            
        text = " ".join(soup.get_text().split())
        return text[:8000] # Safe token limit
    except Exception as e:
        return f"Error fetching site content: {str(e)}"

def format_with_gemini(site_name, site_url, old_text, new_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ""
    
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are a tracking assistant for an Edinburgh charity events newsletter. 
    Compare the OLD text scraped last week with the NEW text scraped this week from the website "{site_name}".
    Identify any newly added upcoming events that were NOT listed in the OLD text. 

    If there are real new events added, format each one strictly using this EXACT structure:
    DD.MM - [Organisation Name] - [Event Title] - [Organisation Name] - [Learn More]([URL])

    Rules for fields:
    - DD.MM: The date of the event in day.month format (e.g., 28.06). If the year is 2026, still output DD.MM. If date is completely missing, write "TBC".
    - [Organisation Name]: Use "{site_name}".
    - [Event Title]: Clean name of the event.
    - The end must explicitly be written as - [Learn More]([URL]) using the precise URL provided below.

    Example of expected format:
    28.06 - {site_name} - Social Sunday - {site_name} - [Learn More]({site_url})

    If no brand-new events have been added, or if only formatting/cookies/dates of the scraper changed, reply with only the exact phrase: "No new events".

    OLD WEEK TEXT:
    {old_text}

    NEW WEEK TEXT:
    {new_text}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(endpoint, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        data = res.json()
        ai_response = data['candidates'][0]['content']['parts'][0]['text'].strip()
        if "No new events" in ai_response:
            return ""
        return ai_response
    except Exception:
        return ""

def main():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {}

    current_history = {}
    new_additions = []

    for name, url in URLS.items():
        print(f"Scraping: {name}...")
        new_text = fetch_page_text(url)
        old_text = history.get(name, "")

        # Always save current text for next check
        current_history[name] = new_text

        # If we have past data and text changed, pass to Free Gemini API to extract details
        if old_text and old_text != new_text:
            formatted_events = format_with_gemini(name, url, old_text, new_text)
            if formatted_events:
                new_additions.append(formatted_events)

    # Save tracking history state back to GitHub repo
    with open(HISTORY_FILE, "w") as f:
        json.dump(current_history, f, indent=4)

    # Compile the final weekly summary document
    with open(OUTPUT_FILE, "w") as f:
        if new_additions:
            f.write("\n".join(new_additions))
        else:
            f.write("No brand new events discovered this week across monitored channels.")

if __name__ == "__main__":
    main()
