#!/usr/bin/env python3
import argparse,json,os,urllib.request,urllib.error,re

MODES=["Learning","Lab","SOC","Pentest","Exam","Interview","Teacher","Project"]

def req(url,method="GET",payload=None,headers=None,timeout=180):
    data=None if payload is None else json.dumps(payload).encode()
    h={"Content-Type":"application/json","Accept":"application/json","User-Agent":"CyberMentorAI-CLI/3.0"}
    if headers:h.update(headers)
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=timeout) as x:return x.status,json.loads(x.read())
    except urllib.error.HTTPError as e:
        raw=e.read().decode("utf-8","replace")
        try:return e.code,json.loads(raw)
        except:return e.code,{"error":{"message":raw or str(e)}}

def out_text(d):
    if isinstance(d,dict) and d.get("output_text"):return str(d["output_text"])
    out=[]
    for item in d.get("output",[]) if isinstance(d,dict) else []:
        for c in item.get("content",[]):
            if isinstance(c,dict) and c.get("text"):out.append(str(c["text"]))
    if out:return "\n".join(out)
    if isinstance(d,dict) and d.get("error"):
        e=d["error"];return str(e.get("message") if isinstance(e,dict) else e)
    return json.dumps(d,indent=2)

def best_model(key):
    c,d=req("https://api.openai.com/v1/models",headers={"Authorization":"Bearer "+key},timeout=30)
    if c>=400:raise RuntimeError(out_text(d))
    ids=[x.get("id","") for x in d.get("data",[]) if x.get("id")]
    ids=[x for x in ids if x.startswith("gpt-") and not any(k in x.lower() for k in ("audio","image","realtime","transcribe","tts","embedding","search","cyber","daybreak"))]
    def rank(mid):
        m=re.search(r"gpt-(\d+)(?:\.(\d+))?",mid)
        major=int(m.group(1)) if m else 0
        minor=int(m.group(2) or 0) if m else 0
        tier=3 if "sol" in mid.lower() else 2 if "terra" in mid.lower() else 1 if "luna" in mid.lower() else 2
        return (major,minor,tier,mid)
    if not ids:raise RuntimeError("No compatible GPT model found.")
    return sorted(ids,key=rank,reverse=True)[0]

def instruct(mode,level):
    return f"You are CyberMentor AI, an advanced cybersecurity tutor and defensive lab mentor. Mode: {mode}. Level: {level}. Be accurate, mark uncertainty, explain commands, and limit practical offensive guidance to authorized systems and training labs."

def openai_chat(q,a):
    key=a.api_key or os.getenv("OPENAI_API_KEY","")
    if not key:raise RuntimeError("No OpenAI API key. Use --api-key or OPENAI_API_KEY.")
    model=a.model or best_model(key)
    payload={"model":model,"instructions":instruct(a.mode,a.level),"input":[{"role":"user","content":q}]}
    c,d=req("https://api.openai.com/v1/responses","POST",payload,{"Authorization":"Bearer "+key})
    if c>=400:raise RuntimeError(out_text(d))
    return out_text(d),model

def ollama_chat(q,a):
    base=a.ollama.rstrip("/")
    model=a.model
    if not model:
        c,d=req(base+"/api/tags",timeout=8)
        if c>=400 or not d.get("models"):raise RuntimeError("No Ollama model found. Install a model first.")
        model=d["models"][0].get("name","")
    msgs=[{"role":"system","content":instruct(a.mode,a.level)},{"role":"user","content":q}]
    c,d=req(base+"/api/chat","POST",{"model":model,"messages":msgs,"stream":False})
    if c>=400:raise RuntimeError(out_text(d))
    return str((d.get("message") or {}).get("content","")),model

def backend_chat(q,a):
    if not a.backend:raise RuntimeError("No backend URL. Use --backend.")
    h={}
    if a.token:h["Authorization"]="Bearer "+a.token
    p={"model":a.model,"instructions":instruct(a.mode,a.level),"input":[{"role":"user","content":q}]}
    c,d=req(a.backend.rstrip("/")+"/api/chat","POST",p,h)
    if c>=400:raise RuntimeError(out_text(d))
    return out_text(d),a.model or "server-selected"

ap=argparse.ArgumentParser(description="CyberMentor AI CLI")
ap.add_argument("--provider",choices=["openai","ollama","backend"],default=os.getenv("CYBERMENTOR_PROVIDER","openai"))
ap.add_argument("--model",default=os.getenv("CYBERMENTOR_MODEL",""))
ap.add_argument("--api-key",default="")
ap.add_argument("--ollama",default=os.getenv("OLLAMA_URL","http://127.0.0.1:11434"))
ap.add_argument("--backend",default=os.getenv("CYBERMENTOR_BACKEND",""))
ap.add_argument("--token",default=os.getenv("CYBERMENTOR_TOKEN",""))
ap.add_argument("--mode",choices=MODES,default="Learning")
ap.add_argument("--level",choices=["Beginner","Intermediate","Advanced"],default="Intermediate")
ap.add_argument("--once")
ap.add_argument("--self-test",action="store_true")
a=ap.parse_args()

if a.self_test:
    assert "SOC" in MODES and "Project" in MODES
    print("CyberMentor AI CLI self-test passed")
    raise SystemExit(0)

def ask(q):
    try:
        if a.provider=="openai":ans,model=openai_chat(q,a)
        elif a.provider=="ollama":ans,model=ollama_chat(q,a)
        else:ans,model=backend_chat(q,a)
        print(ans)
    except Exception as e:
        s=str(e)
        if "No OpenAI API key" in s:print("Setup required: provide your OpenAI API key with --api-key or OPENAI_API_KEY.")
        elif "No Ollama model" in s:print("Setup required: start Ollama and install a model, or switch provider.")
        else:print("Request failed:",s)

if a.once:ask(a.once)
else:
    print(f"CyberMentor AI CLI | provider={a.provider} | mode={a.mode} | level={a.level}")
    print("Type /quit to exit.")
    while True:
        try:q=input("cybermentor> ").strip()
        except (EOFError,KeyboardInterrupt):break
        if q in ("/quit","quit","exit"):break
        if q:ask(q)
