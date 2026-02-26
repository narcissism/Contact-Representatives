import requests, json, os

PROP_KEY = "YOUR_PROPUBLICA_KEY"
FEC_KEY = "YOUR_FEC_KEY"

def get_members(chamber):
    url=f"https://api.propublica.org/congress/v1/118/{chamber}/members.json"
    r=requests.get(url,headers={"X-API-Key":PROP_KEY}).json()
    return r["results"][0]["members"]

def get_fec_totals(name):
    url="https://api.open.fec.gov/v1/candidates/search/"
    r=requests.get(url,params={
        "api_key":FEC_KEY,
        "q":name
    }).json()
    try:
        return r["results"][0]["total_receipts"]
    except:
        return None

members=[]

for chamber in ["house","senate"]:
    for m in get_members(chamber):
        pac=get_fec_totals(m["last_name"])

        members.append({
            "name":m["first_name"]+" "+m["last_name"],
            "position":chamber.title(),
            "state":m["state"],
            "party":m["party"],
            "committees":"",
            "pac_total":pac,
            "dc_phone":m.get("phone")
        })

open("data.js","w").write("const MEMBERS="+json.dumps(members))
print("data.js updated")
