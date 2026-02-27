import requests, yaml, json, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"

HEADERS = {"User-Agent":"Mozilla/5.0"}

CONTACT_PATHS = [
    "contact",
    "contact/offices",
    "about/offices",
    "offices"
]

PHONE_RE = re.compile(r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}")
ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)


def fetch_html(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=10).text
    except:
        return ""


def try_contact_pages(base_url):
    pages = [base_url]
    for p in CONTACT_PATHS:
        pages.append(urljoin(base_url, p))

    for url in pages:
        html = fetch_html(url)
        if html and len(html) > 5000:
            return html
    return ""


def extract_info(html, state):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    phones = list(set(PHONE_RE.findall(text)))
    zips = list(set(ZIP_RE.findall(text)))
    emails = list(set(EMAIL_RE.findall(text)))

    # remove DC zips
    zips = [z for z in zips if not z.startswith("205")]

    return phones, emails, zips


def main():
    data = yaml.safe_load(requests.get(LEGISLATORS_URL).text)
    members = []

    for leg in data:
        term = leg["terms"][-1]

        name = f"{leg['name']['first']} {leg['name']['last']}"
        state = term["state"]
        website = term.get("url")

        html = try_contact_pages(website) if website else ""
        phones, emails, zips = extract_info(html, state) if html else ([],[],[])

        bioguide = leg["id"].get("bioguide")
        photo = f"https://www.govtrack.us/static/legislator-photos/{bioguide}-200px.jpeg" if bioguide else None

        members.append({
            "name": name,
            "state": state,
            "party": term["party"],
            "chamber": term["type"],
            "website": website,
            "phones": phones,
            "emails": emails,
            "home_state_zips": zips,
            "photo": photo
        })

        print("✔", name)

    with open("members.json","w") as f:
        json.dump(members, f, indent=2)

    print("Saved", len(members))


if __name__ == "__main__":
    main()
