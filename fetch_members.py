import requests
import yaml
import json

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"

def main():
    print("Downloading legislators...")
    r = requests.get(LEGISLATORS_URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    data = yaml.safe_load(r.text)

    members = []

    for leg in data:
        term = leg["terms"][-1]

        members.append({
            "name": f"{leg['name']['first']} {leg['name']['last']}",
            "state": term["state"],
            "party": term["party"],
            "chamber": term["type"],
            "website": term.get("url")
        })

    with open("members.json", "w") as f:
        json.dump(members, f, indent=2)

    print("Saved", len(members), "members")

if __name__ == "__main__":
    main()
