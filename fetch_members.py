import requests
import yaml
import json
import os

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"
FEC_API_KEY = os.getenv("FEC_API_KEY")

def get_fec_totals(name, state):
    if not FEC_API_KEY:
        return None

    try:
        search = requests.get(
            "https://api.open.fec.gov/v1/candidates/search/",
            params={
                "api_key": FEC_API_KEY,
                "q": name,
                "state": state,
                "per_page": 1
            }
        ).json()

        if not search["results"]:
            return None

        cid = search["results"][0]["candidate_id"]

        totals = requests.get(
            f"https://api.open.fec.gov/v1/candidate/{cid}/totals/",
            params={"api_key": FEC_API_KEY}
        ).json()

        if totals["results"]:
            latest = totals["results"][0]
            return {
                "receipts": latest.get("receipts"),
                "pacs": latest.get("contributions_from_other_political_committees")
            }

    except:
        return None

def main():
    r = requests.get(LEGISLATORS_URL, headers={"User-Agent":"Mozilla/5.0"})
    data = yaml.safe_load(r.text)

    members = []

    for leg in data:
        term = leg["terms"][-1]

        name = f"{leg['name']['first']} {leg['name']['last']}"
        state = term["state"]
        chamber = term["type"]
        party = term["party"]
        phone = term.get("phone")

        bioguide = leg["id"]["bioguide"]
        photo = f"https://www.govtrack.us/static/legislator-photos/{bioguide}-200px.jpeg"

        fec = get_fec_totals(name, state)

        members.append({
            "name": name,
            "state": state,
            "party": party,
            "chamber": chamber,
            "phone": phone,
            "photo": photo,
            "website": term.get("url"),
            "fec": fec
        })

    with open("members.json","w") as f:
        json.dump(members, f, indent=2)

    print("Saved", len(members), "members")

if __name__ == "__main__":
    main()
