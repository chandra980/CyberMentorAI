#!/usr/bin/env python3
import argparse,json,os,urllib.request
def post(url,payload,token=""):
    h={"Content-Type":"application/json"}
    if token:h["Authorization"]="Bearer "+token
    r=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=h,method="POST")
    with urllib.request.urlopen(r,timeout=180) as x:return json.loads(x.read())
def text(d):
    for item in d.get("output",[]):
        for c in item.get("content",[]):
            if c.get("text"):return c["text"]
    return json.dumps(d,indent=2)
ap=argparse.ArgumentParser(description="CyberMentor AI CLI")
ap.add_argument("--backend",default=os.getenv("CYBERMENTOR_BACKEND","http://127.0.0.1:8787"))
ap.add_argument("--token",default=os.getenv("CYBERMENTOR_TOKEN",""))
ap.add_argument("--provider",default=os.getenv("AI_PROVIDER","openai"))
ap.add_argument("--model",default=os.getenv("OPENAI_MODEL","gpt-5.6"))
ap.add_argument("--mode",default="Learning")
ap.add_argument("--level",default="Intermediate")
ap.add_argument("--once")
a=ap.parse_args()
def ask(q):
    p={"provider":a.provider,"model":a.model,"instructions":f"Mode: {a.mode}. Level: {a.level}.","input":[{"role":"user","content":q}]}
    try:print(text(post(a.backend.rstrip("/")+"/api/chat",p,a.token)))
    except Exception as e:print("Error:",e)
if a.once:ask(a.once)
else:
    print("CyberMentor AI CLI. Type /quit to exit.")
    while True:
        try:q=input("cybermentor> ").strip()
        except (EOFError,KeyboardInterrupt):break
        if q in ("/quit","exit","quit"):break
        if q:ask(q)
