import requests, yaml, json, re
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urljoin

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"
HEADERS = {"User-Agent":"Mozilla/5.0"}

PHONE_RE = re.compile(r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}")
ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return ""

def find_contact_page(base_url):
    html = fetch(base_url)
    if not html:
        return base_url

    soup = BeautifulSoup(html, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if "contact" in href or "office" in href:
            return urljoin(base_url, a["href"])

    return base_url

def scrape_contact(url):
    html = fetch(url)
    if not html:
        return [], []

    phones = list(set(PHONE_RE.findall(html)))
    zips = list(set(ZIP_RE.findall(html)))

    # remove DC numbers
    phones = [p for p in phones if not p.startswith("202")]

    return phones, zips

def main():
    data = yaml.safe_load(requests.get(LEGISLATORS_URL).text)
    members = []

    for leg in data:
        term = leg["terms"][-1]
        website = term.get("url")

        contact_page = find_contact_page(website) if website else None
        phones, zips = scrape_contact(contact_page) if contact_page else ([], [])

        bioguide = leg["id"].get("bioguide")
        photo = f"https://www.govtrack.us/static/legislator-photos/{bioguide}-200px.jpeg" if bioguide else None

        members.append({
            "name": f"{leg['name']['first']} {leg['name']['last']}",
            "state": term["state"],
            "party": term["party"],
            "chamber": term["type"],
            "website": website,
            "contact_page": contact_page,
            "phones": phones,
            "zipcodes": zips,
            "photo": photo
        })

        print("✔", leg["name"]["last"])
        sleep(0.7)

    with open("members.json","w") as f:
        json.dump(members, f, indent=2)

    print("Saved", len(members))

if __name__ == "__main__":
    main()
