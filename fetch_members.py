import requests, yaml, json, re

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"
HEADERS = {"User-Agent":"Mozilla/5.0"}

def scrape_contact(url):
    if not url:
        return None, None

    try:
        html = requests.get(url, headers=HEADERS, timeout=10).text

        phone = re.search(r"(\\(?\\d{3}\\)?[-\\.\\s]\\d{3}[-\\.\\s]\\d{4})", html)
        zipc = re.search(r"\\b\\d{5}(?:-\\d{4})?\\b", html)

        return phone.group(0) if phone else None, zipc.group(0) if zipc else None

    except:
        return None, None


def main():
    data = yaml.safe_load(requests.get(LEGISLATORS_URL, headers=HEADERS).text)

    members = []

    for leg in data:
        term = leg["terms"][-1]

        name = f"{leg['name']['first']} {leg['name']['last']}"
        website = term.get("url")

        phone, zipc = scrape_contact(website)

        bioguide = leg["id"]["bioguide"]
        photo = f"https://www.govtrack.us/static/legislator-photos/{bioguide}-200px.jpeg"

        members.append({
            "name": name,
            "state": term["state"],
            "party": term["party"],
            "chamber": term["type"],
            "website": website,
            "phone": phone,
            "zipcode": zipc,
            "photo": photo
        })

    with open("members.json","w") as f:
        json.dump(members, f, indent=2)

    print("Saved", len(members))

if __name__ == "__main__":
    main()
