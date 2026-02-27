import requests, yaml, json, re
from bs4 import BeautifulSoup
from time import sleep

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"
HEADERS = {"User-Agent":"Mozilla/5.0"}

PHONE_RE = re.compile(r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}")

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.text
    except:
        return ""
    return ""

def congress_url(bioguide):
    return f"https://www.congress.gov/member/{bioguide}"

def scrape_congress_phones(bioguide, state):
    url = congress_url(bioguide)
    html = fetch(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    phones = list(set(PHONE_RE.findall(text)))

    # remove DC numbers (202 area code)
    phones = [p for p in phones if not p.startswith("202")]

    return phones

def main():
    data = yaml.safe_load(requests.get(LEGISLATORS_URL).text)
    members = []

    for leg in data:
        term = leg["terms"][-1]
        name = f"{leg['name']['first']} {leg['name']['last']}"
        state = term["state"]
        chamber = term["type"]
        party = term["party"]

        bioguide = leg["id"].get("bioguide")

        phones = scrape_congress_phones(bioguide, state) if bioguide else []

        photo = f"https://www.govtrack.us/static/legislator-photos/{bioguide}-200px.jpeg" if bioguide else None

        members.append({
            "name": name,
            "state": state,
            "party": party,
            "chamber": chamber,
            "phones": phones,
            "photo": photo
        })

        print("✔", name)
        sleep(0.5)   # avoid rate limiting

    with open("members.json","w") as f:
        json.dump(members, f, indent=2)

    print("Saved", len(members))

if __name__ == "__main__":
    main()
