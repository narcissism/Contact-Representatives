import requests, yaml, json, re
from bs4 import BeautifulSoup

LEGISLATORS_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml"
HEADERS = {"User-Agent":"Mozilla/5.0"}

PHONE_RE = re.compile(r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}")

def get_house_phones():
    url = "https://clerk.house.gov/members"
    html = requests.get(url, headers=HEADERS).text
    phones = PHONE_RE.findall(html)
    return phones

def get_senate_phones():
    url = "https://www.senate.gov/senators/senators-contact.htm"
    html = requests.get(url, headers=HEADERS).text
    phones = PHONE_RE.findall(html)
    return phones

def main():
    data = yaml.safe_load(requests.get(LEGISLATORS_URL).text)

    house_phones = get_house_phones()
    senate_phones = get_senate_phones()

    members = []

    for leg in data:
        term = leg["terms"][-1]

        members.append({
            "name": f"{leg['name']['first']} {leg['name']['last']}",
            "state": term["state"],
            "party": term["party"],
            "chamber": term["type"],
            "phones": house_phones if term["type"]=="rep" else senate_phones
        })

    with open("members.json","w") as f:
        json.dump(members,f,indent=2)

    print("done")

main()
