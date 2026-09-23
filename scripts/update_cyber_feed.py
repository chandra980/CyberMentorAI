#!/usr/bin/env python3
import json, urllib.request, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"cyber_feed.json"
def get(url):
    r=urllib.request.Request(url,headers={"User-Agent":"CyberMentorAI-Feed/2.0","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=45) as x:return json.loads(x.read())
items=[]
try:
    kev=get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    for v in (kev.get("vulnerabilities") or [])[:80]:
        items.append({"id":v.get("cveID"),"title":f"{v.get('cveID','')} - {v.get('vulnerabilityName','')}",
        "source":"CISA KEV","date":v.get("dateAdded"),"vendor":v.get("vendorProject"),"product":v.get("product"),
        "summary":v.get("shortDescription"),"action":v.get("requiredAction"),"due":v.get("dueDate")})
except Exception as e:
    items.append({"title":"CISA feed unavailable","source":"system","summary":str(e)})
# NVD recent CVEs (best-effort; no API key required but rate-limited)
try:
    now=datetime.datetime.now(datetime.timezone.utc)
    start=now-datetime.timedelta(days=7)
    fmt=lambda d:d.strftime("%Y-%m-%dT%H:%M:%S.000")
    url="https://services.nvd.nist.gov/rest/json/cves/2.0/?pubStartDate="+fmt(start)+"&pubEndDate="+fmt(now)+"&resultsPerPage=40"
    nvd=get(url)
    for wrap in nvd.get("vulnerabilities",[])[:40]:
        c=wrap.get("cve",{}); desc=""
        for d in c.get("descriptions",[]):
            if d.get("lang")=="en":desc=d.get("value","");break
        items.append({"id":c.get("id"),"title":c.get("id"),"source":"NIST NVD","date":c.get("published"),"summary":desc[:1200]})
except Exception as e:
    items.append({"title":"NVD feed unavailable","source":"system","summary":str(e)})
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps({"generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"items":items},ensure_ascii=False,indent=2),encoding="utf-8")
print("wrote",len(items),"items to",OUT)
