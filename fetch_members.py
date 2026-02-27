import requests, yaml, json, os

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"
FEC_API_KEY = os.getenv("jBzdbBdTatdkWAeRfRuOCuxIkAWhp4kkS14TyONx")

def load_legislators():
    print("Downloading legislators...")
    r = requests.get(LEGISLATORS_URL, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    return yaml.safe_load(r.text)

def main():
    data = load_legislators()
    members = []

    for leg in data:
        term = leg["terms"][-1]

        name = f"{leg['name']['first']} {leg['name']['last']}"
        state = term["state"]
        party = term["party"]
        chamber = term["type"]

        members.append({
            "name": name,
            "state": state,
            "party": party,
            "chamber": chamber,
            "website": term.get("url"),
            "fec": None
        })

    with open("members.json","w") as f:
        json.dump(members, f, indent=2)

    print("Saved", len(members), "members")

if __name__ == "__main__":
    main()
