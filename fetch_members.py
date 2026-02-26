import requests, json, re

PROP_KEY="YOUR_PROPUBLICA_KEY"

def clean_phone(p):
    if not p: return ""
    return re.sub(r"\D","",p)

def get_members(chamber):
    url=f"https://api.propublica.org/congress/v1/118/{chamber}/members.json"
    r=requests.get(url,headers={"X-API-Key":PROP_KEY}).json()
    return r["results"][0]["members"]

members=[]

for chamber in ["house","senate"]:
    for m in get_members(chamber):

        members.append({
            "name":f"{m['first_name']} {m['last_name']}",
            "position":chamber.title(),
            "state":m["state"],
            "party":m["party"],
            "committees":"",
            "pac_total":"",
            "dc_phone":clean_phone(m.get("phone")),
            "state_phone":"",
            "email":""
        })

members=sorted(members,key=lambda x:x["state"])

open("data.js","w").write(
    "const MEMBERS="+json.dumps(members,indent=2)
)

print("data.js updated")
