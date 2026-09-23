#!/usr/bin/env python3
import json, os, ssl, time, urllib.request, urllib.error, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOST=os.getenv("HOST","127.0.0.1")
PORT=int(os.getenv("PORT","8787"))
PROVIDER=os.getenv("AI_PROVIDER","openai").lower()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY","")
OPENAI_MODEL=os.getenv("OPENAI_MODEL","")
OLLAMA_URL=os.getenv("OLLAMA_URL","http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL","")
COMPAT_BASE_URL=os.getenv("COMPAT_BASE_URL","").rstrip("/")
COMPAT_API_KEY=os.getenv("COMPAT_API_KEY","")
APP_ACCESS_TOKEN=os.getenv("APP_ACCESS_TOKEN","")
REPO="chandra980/CyberMentorAI"
BASE_PROMPT=(ROOT/"assistant_prompt.txt").read_text(encoding="utf-8") if (ROOT/"assistant_prompt.txt").exists() else "You are CyberMentor AI."

def req_json(url, method="GET", payload=None, headers=None, timeout=120):
    body=None if payload is None else json.dumps(payload).encode()
    h={"Accept":"application/json","Content-Type":"application/json","User-Agent":"CyberMentorAI/2.0"}
    if headers:h.update(headers)
    r=urllib.request.Request(url,data=body,method=method,headers=h)
    try:
        with urllib.request.urlopen(r,timeout=timeout,context=ssl.create_default_context()) as x:
            raw=x.read().decode("utf-8","replace")
            return x.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raw=e.read().decode("utf-8","replace")
        try:return e.code,json.loads(raw)
        except:return e.code,{"error":raw or str(e)}

def send(h,code,obj):
    b=json.dumps(obj,ensure_ascii=False).encode()
    h.send_response(code);h.send_header("Content-Type","application/json; charset=utf-8")
    h.send_header("Content-Length",str(len(b)));h.send_header("Access-Control-Allow-Origin","*")
    h.send_header("Access-Control-Allow-Headers","Content-Type, Authorization");h.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
    h.end_headers();h.wfile.write(b)

def choose_openai_model(ids):
    ids=[x for x in ids if isinstance(x,str) and x.startswith("gpt-")]
    ids=[x for x in ids if not any(k in x.lower() for k in ("audio","image","realtime","transcribe","tts","embedding","search","cyber","daybreak"))]
    def rank(mid):
        m=re.search(r"gpt-(\d+)(?:\.(\d+))?",mid)
        major=int(m.group(1)) if m else 0
        minor=int(m.group(2) or 0) if m else 0
        tier=3 if "sol" in mid.lower() else 2 if "terra" in mid.lower() else 1 if "luna" in mid.lower() else 2
        return (major,minor,tier,mid)
    ordered=sorted(ids,key=rank,reverse=True)
    return ordered[0] if ordered else ""

def resolve_openai_model():
    if OPENAI_MODEL.strip():return OPENAI_MODEL.strip()
    code,d=req_json("https://api.openai.com/v1/models",headers={"Authorization":"Bearer "+OPENAI_API_KEY},timeout=30)
    if code>=400:return ""
    return choose_openai_model([x.get("id") for x in d.get("data",[]) if x.get("id")])

def normalized(text,model,provider):
    return {"id":f"cybermentor-{int(time.time())}","model":model,"provider":provider,
            "output":[{"type":"message","role":"assistant","content":[{"type":"output_text","text":text}]}]}

def to_messages(p):
    out=[{"role":"system","content":BASE_PROMPT+"\n\n"+str(p.get("instructions",""))}]
    for m in p.get("input",[]) or []:
        c=m.get("content","")
        if isinstance(c,list): c="\n".join(str(x.get("text","")) if isinstance(x,dict) else str(x) for x in c)
        out.append({"role":m.get("role","user"),"content":str(c)})
    return out

def chat(p):
    provider=str(p.pop("provider",PROVIDER)).lower()
    if provider=="openai":
        if not OPENAI_API_KEY:return 503,{"error":{"message":"OPENAI_API_KEY is not configured."}}
        p=dict(p);p["instructions"]=BASE_PROMPT+"\n\n"+str(p.get("instructions",""))
        model=str(p.get("model","")).strip() or resolve_openai_model()
        if not model:return 503,{"error":{"message":"No compatible OpenAI model is available for this API key."}}
        p["model"]=model
        return req_json("https://api.openai.com/v1/responses","POST",p,{"Authorization":"Bearer "+OPENAI_API_KEY},180)
    if provider=="ollama":
        model=str(p.get("model") or OLLAMA_MODEL).strip()
        if not model:
            c,t=req_json(OLLAMA_URL+"/api/tags",timeout=5)
            if c>=400 or not t.get("models"):return 503,{"error":{"message":"No Ollama model is installed."}}
            model=str(t["models"][0].get("name",""))
        code,d=req_json(OLLAMA_URL+"/api/chat","POST",{"model":model,"messages":to_messages(p),"stream":False},timeout=180)
        if code>=400:return code,d
        return 200,normalized(str((d.get("message") or {}).get("content","")),model,"ollama")
    if provider in ("compatible","openai-compatible"):
        if not COMPAT_BASE_URL:return 503,{"error":{"message":"COMPAT_BASE_URL is not configured."}}
        model=str(p.get("model",""))
        hd={"Authorization":"Bearer "+COMPAT_API_KEY} if COMPAT_API_KEY else {}
        code,d=req_json(COMPAT_BASE_URL+"/v1/chat/completions","POST",{"model":model,"messages":to_messages(p)},hd,180)
        if code>=400:return code,d
        try:t=d["choices"][0]["message"]["content"]
        except:t=json.dumps(d)
        return 200,normalized(str(t),model,"compatible")
    return 400,{"error":{"message":"Unsupported provider: "+provider}}

class H(BaseHTTPRequestHandler):
    def log_message(self,fmt,*a): print("[%s] %s"%(self.log_date_time_string(),fmt%a))
    def do_OPTIONS(self): send(self,204,{})
    def do_GET(self):
        if self.path=="/api/health":return send(self,200,{"ok":True,"provider":PROVIDER,"repo":REPO})
        if self.path=="/api/feed":
            f=ROOT/"data/cyber_feed.json";return send(self,200,json.loads(f.read_text()) if f.exists() else {"items":[]})
        if self.path=="/api/update":
            c,d=req_json(f"https://api.github.com/repos/{REPO}/releases/latest",timeout=20);return send(self,c,d)
        if self.path=="/api/models":
            out={"provider":PROVIDER,"models":[]}
            if OPENAI_API_KEY:
                c,d=req_json("https://api.openai.com/v1/models",headers={"Authorization":"Bearer "+OPENAI_API_KEY},timeout=30)
                if c<400:out["models"]=sorted([x.get("id") for x in d.get("data",[]) if x.get("id")])
            try:
                c,d=req_json(OLLAMA_URL+"/api/tags",timeout=3)
                if c<400:out["ollama_models"]=[x.get("name") for x in d.get("models",[])]
            except:pass
            return send(self,200,out)
        send(self,404,{"error":"Not found"})
    def do_POST(self):
        if self.path!="/api/chat":return send(self,404,{"error":"Not found"})
        if APP_ACCESS_TOKEN and self.headers.get("Authorization","")!="Bearer "+APP_ACCESS_TOKEN:return send(self,401,{"error":"Invalid app access token"})
        try:
            n=int(self.headers.get("Content-Length","0"));p=json.loads(self.rfile.read(n))
        except Exception as e:return send(self,400,{"error":"Invalid request: "+str(e)})
        c,d=chat(p);send(self,c,d)

if __name__=="__main__":
    print(f"CyberMentor AI backend: http://{HOST}:{PORT} provider={PROVIDER}")
    if HOST not in ("127.0.0.1","localhost") and not APP_ACCESS_TOKEN: print("WARNING: set APP_ACCESS_TOKEN before exposing this server.")
    ThreadingHTTPServer((HOST,PORT),H).serve_forever()
