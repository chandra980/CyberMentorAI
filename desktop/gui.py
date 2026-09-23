#!/usr/bin/env python3
import argparse, json, os, platform, threading, urllib.request, urllib.error, webbrowser, re
from pathlib import Path

APP_NAME="CyberMentor AI"
OWNER_NAME="Chandra Kumar Yadav"
REPO="chandra980/CyberMentorAI"
CONFIG_DIR=Path.home()/".cybermentor"
CONFIG_FILE=CONFIG_DIR/"config.json"
HISTORY_FILE=CONFIG_DIR/"history.json"
APP_VERSION="3.1"
KEY_SERVICE="CyberMentorAI"
DEFAULT_FEED=f"https://raw.githubusercontent.com/{REPO}/main/data/cyber_feed.json"

MODES={
"Auto":"Automatically route the user request to the best CyberMentor workflow.",
"Learning":"Teach with definition, simple explanation, analogy, technical detail, examples, attack/defense perspective, common mistakes and a practice question.",
"Lab":"Authorized Lab Mode: objective, prerequisites, safe lab, topology, tools, steps, commands, expected results, explanation, troubleshooting, cleanup and challenge.",
"SOC":"SOC Analyst Mode: triage, evidence, IOCs, timeline, MITRE ATT&CK, false positives, severity, containment, remediation and reporting. Do not reveal scenario answers immediately.",
"Pentest":"Pentest Learning Mode: scope/authorization, recon, enumeration, vulnerability discovery, validation, exploitation only in authorized labs, privilege escalation concepts, evidence, remediation and reporting.",
"Exam":"Exam Coach Mode: revision, one question at a time, marking, correction, weak-area tracking and progressive difficulty.",
"Interview":"Interview Coach Mode: one question at a time, assessment, improved answer, terminology and increasing difficulty.",
"Teacher":"Teacher Mode: classroom-ready lesson plan, objectives, analogy, technical explanation, examples, activity/lab, differentiation, assessment, homework, answer key and next lesson.",
"Project":"Project Mode: problem statement, architecture, stack, phases, security considerations, testing, expected output, documentation and presentation."
}
TOPICS=["Networking","TCP/IP","OSI Model","Linux","Windows","Cryptography","Web Security","Cloud Security","IAM","SOC","SIEM","EDR","IDS/IPS","Threat Intel","Incident Response","Digital Forensics","OWASP","Active Directory","Python","PowerShell","SQL","API Security","Container Security","Threat Hunting","MITRE ATT&CK","Wireshark","Nmap","Burp Suite","Zeek","Suricata","Splunk","Sysmon","Volatility","YARA","Sigma"]

def load_cfg():
    base={"provider":"OpenAI","model":"","model_profile":"Auto Best","ollama_url":"http://127.0.0.1:11434","backend_url":"","backend_token":"","mode":"Auto","level":"Intermediate","language":"Auto","detail":"Professional"}
    try:
        base.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    except Exception:
        pass
    return base

def save_cfg(cfg):
    CONFIG_DIR.mkdir(parents=True,exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg,indent=2),encoding="utf-8")
    try: os.chmod(CONFIG_FILE,0o600)
    except Exception: pass

def load_history():
    try:
        data=json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return [(str(x.get("role","assistant")),str(x.get("text",""))) for x in data[-200:] if isinstance(x,dict)]
    except Exception:
        return []

def save_history(history):
    CONFIG_DIR.mkdir(parents=True,exist_ok=True)
    data=[{"role":r,"text":t} for r,t in history[-200:]]
    HISTORY_FILE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    try: os.chmod(HISTORY_FILE,0o600)
    except Exception: pass

def get_secret():
    env=os.getenv("OPENAI_API_KEY","").strip()
    if env:return env
    try:
        import keyring
        return (keyring.get_password(KEY_SERVICE,"openai") or "").strip()
    except Exception:
        return ""

def set_secret(value):
    try:
        import keyring
        if value: keyring.set_password(KEY_SERVICE,"openai",value)
        else:
            try:keyring.delete_password(KEY_SERVICE,"openai")
            except Exception:pass
        return True
    except Exception:
        return False

def req_json(url,method="GET",payload=None,headers=None,timeout=120):
    body=None if payload is None else json.dumps(payload).encode("utf-8")
    h={"Accept":"application/json","Content-Type":"application/json","User-Agent":"CyberMentorAI-Desktop/3.0"}
    if headers:h.update(headers)
    r=urllib.request.Request(url,data=body,method=method,headers=h)
    try:
        with urllib.request.urlopen(r,timeout=timeout) as x:
            raw=x.read().decode("utf-8","replace")
            return x.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raw=e.read().decode("utf-8","replace")
        try:d=json.loads(raw)
        except:d={"error":{"message":raw or str(e)}}
        return e.code,d

def extract_text(d):
    if isinstance(d,dict) and d.get("output_text"):return str(d["output_text"])
    out=[]
    for item in (d.get("output",[]) if isinstance(d,dict) else []):
        for c in item.get("content",[]):
            if isinstance(c,dict) and c.get("text"):out.append(str(c["text"]))
    if out:return "\n".join(out)
    if isinstance(d,dict) and "choices" in d:
        try:return str(d["choices"][0]["message"]["content"])
        except Exception:pass
    if isinstance(d,dict) and d.get("error"):
        e=d["error"];return str(e.get("message") if isinstance(e,dict) else e)
    return json.dumps(d,ensure_ascii=False,indent=2)

def choose_model(ids, mode="Learning", profile="Auto Best"):
    ids=sorted({x for x in ids if isinstance(x,str) and x and x.startswith("gpt-")})
    excluded=("audio","image","realtime","transcribe","tts","search","embedding")
    ids=[x for x in ids if not any(k in x.lower() for k in excluded)]
    cyber_modes={"Lab","SOC","Pentest"}
    if profile=="Cyber Specialized" and mode in cyber_modes:
        specialized=[x for x in ids if "cyber" in x.lower() or "daybreak" in x.lower()]
        if specialized:return sorted(specialized,reverse=True)[0]
    general=[x for x in ids if "cyber" not in x.lower() and "daybreak" not in x.lower()]
    def rank(mid):
        m=re.search(r"gpt-(\d+)(?:\.(\d+))?",mid)
        major=int(m.group(1)) if m else 0
        minor=int(m.group(2) or 0) if m else 0
        tier=3 if "sol" in mid.lower() else 2 if "terra" in mid.lower() else 1 if "luna" in mid.lower() else 2
        return (major,minor,tier,mid)
    ordered=sorted(general,key=rank,reverse=True)
    if not ordered:return ""
    if profile=="Economy":
        same=sorted(ordered,key=lambda x:(rank(x)[0],rank(x)[1],0 if "luna" in x.lower() else 1 if "terra" in x.lower() else 2, x),reverse=True)
        return same[0]
    if profile=="Balanced":
        latest_major,latest_minor=rank(ordered[0])[:2]
        candidates=[x for x in ordered if rank(x)[:2]==(latest_major,latest_minor)]
        terra=[x for x in candidates if "terra" in x.lower()]
        return terra[0] if terra else candidates[0]
    return ordered[0]

def auto_route_mode(text):
    x=text.lower()
    if any(k in x for k in ("interview","mock interview","job interview")):return "Interview"
    if any(k in x for k in ("lesson plan","teach my class","students","homework","teacher mode","faculty")):return "Teacher"
    if any(k in x for k in ("exam","mcq","quiz","revision","question paper")):return "Exam"
    if any(k in x for k in ("project","capstone","architecture","build a tool")):return "Project"
    if any(k in x for k in ("dvwa","juice shop","webgoat","metasploitable","lab mode","practice lab","practice environment")):return "Lab"
    if any(k in x for k in ("pentest","penetration test","recon","enumeration","vulnerability assessment")):return "Pentest"
    if any(k in x for k in ("alert","event log","ioc","siem","incident","soc","sysmon","suspicious process","edr")):return "SOC"
    return "Learning"

def friendly_error(exc_or_text):
    s=str(exc_or_text)
    low=s.lower()
    if "10061" in low or "connection refused" in low:return "AI engine is not running. Open Settings and choose OpenAI, Ollama, or a reachable Secure Backend."
    if "401" in low or "unauthorized" in low or "invalid api key" in low:return "The API key was rejected. Open Settings and save a valid key."
    if "429" in low or "quota" in low or "rate limit" in low:return "The AI provider is busy or the account quota was reached. Try again shortly or switch provider/model."
    if "timed out" in low:return "The request took too long. Check internet/provider status and try again."
    if "urlopen error" in low or "network" in low:return "Network connection failed. Check internet access or the configured server address."
    return "The AI request could not be completed. Open Settings, verify the provider/model, then retry."

def system_instruction(mode,level,cfg=None):
    cfg=cfg or {}
    language=cfg.get("language","Auto")
    detail=cfg.get("detail","Professional")
    return f"""You are CyberMentor AI, an advanced cybersecurity professor, ethical hacking tutor, SOC mentor, network security instructor, digital forensics tutor, authorized penetration testing lab coach and exam coach.
Current mode: {mode}. Student level: {level}. Mode rules: {MODES.get(mode,MODES['Learning'])}
Response language: {language}. Response depth: {detail}.
Use clean headings, short sections, tables for comparisons, numbered steps for procedures, and code blocks for commands. For complex answers end with KEY TAKEAWAY.
Be accurate and clearly mark uncertainty. Never invent CVEs, advisories, statistics or tool capabilities. When teaching commands explain purpose, syntax, important options, example, expected output and security considerations. Practical security guidance must stay within systems the user owns, has explicit authorization to test, or intentionally vulnerable training labs. Prefer defensive, educational and remediation-focused guidance."""

def provider_chat(cfg,user_text,history):
    p=cfg["provider"]
    mode,level=cfg["mode"],cfg["level"]
    instructions=system_instruction(mode,level)
    recent=history[-10:]
    if p=="OpenAI":
        key=get_secret()
        if not key:raise RuntimeError("SETUP_REQUIRED")
        model=cfg.get("model","").strip()
        if not model:
            code,d=req_json("https://api.openai.com/v1/models",headers={"Authorization":"Bearer "+key},timeout=25)
            if code>=400:raise RuntimeError(extract_text(d))
            model=choose_model([x.get("id") for x in d.get("data",[])],mode,cfg.get("model_profile","Auto Best"))
            if not model:raise RuntimeError("No compatible model was returned by the provider.")
            cfg["model"]=model;save_cfg(cfg)
        payload={"model":model,"instructions":instructions,"input":[*recent,{"role":"user","content":user_text}]}
        code,d=req_json("https://api.openai.com/v1/responses","POST",payload,{"Authorization":"Bearer "+key},180)
        if code>=400:raise RuntimeError(extract_text(d))
        return extract_text(d)
    if p=="Ollama":
        base=cfg.get("ollama_url","http://127.0.0.1:11434").rstrip("/")
        model=cfg.get("model","").strip()
        if not model:
            code,d=req_json(base+"/api/tags",timeout=5)
            if code>=400 or not d.get("models"):raise RuntimeError("No Ollama model is installed.")
            model=d["models"][0].get("name","")
            cfg["model"]=model;save_cfg(cfg)
        msgs=[{"role":"system","content":instructions},*recent,{"role":"user","content":user_text}]
        code,d=req_json(base+"/api/chat","POST",{"model":model,"messages":msgs,"stream":False},timeout=180)
        if code>=400:raise RuntimeError(extract_text(d))
        return str((d.get("message") or {}).get("content",""))
    base=cfg.get("backend_url","").strip().rstrip("/")
    if not base:raise RuntimeError("SETUP_REQUIRED")
    h={}
    tok=cfg.get("backend_token","").strip()
    if tok:h["Authorization"]="Bearer "+tok
    payload={"model":cfg.get("model",""),"instructions":instructions,"input":[*recent,{"role":"user","content":user_text}]}
    code,d=req_json(base+"/api/chat","POST",payload,h,180)
    if code>=400:raise RuntimeError(extract_text(d))
    return extract_text(d)

def self_test():
    cfg=load_cfg()
    assert "provider" in cfg and "mode" in cfg and len(TOPICS)>20
    assert "Authorized Lab Mode" in MODES["Lab"]
    assert auto_route_mode("suspicious sysmon alert")=="SOC"
    assert choose_model(["gpt-7-luna","gpt-6-sol","gpt-5.6-sol"],"Learning","Auto Best")=="gpt-7-luna"
    print("CyberMentor AI desktop self-test passed")
    return 0

def main():
    ap=argparse.ArgumentParser(add_help=False);ap.add_argument("--self-test",action="store_true");a,_=ap.parse_known_args()
    if a.self_test:return self_test()
    import customtkinter as ctk
    try:import keyring
    except Exception:keyring=None
    ctk.set_appearance_mode("dark");ctk.set_default_color_theme("dark-blue")
    cfg=load_cfg();history=load_history()

    app=ctk.CTk();app.title(APP_NAME);app.geometry("1180x760");app.minsize(920,620)
    app.configure(fg_color="#06111d")
    app.grid_columnconfigure(1,weight=1);app.grid_rowconfigure(0,weight=1)

    side=ctk.CTkFrame(app,width=230,corner_radius=0,fg_color="#081826");side.grid(row=0,column=0,sticky="nsew")
    ctk.CTkLabel(side,text="CYBERMENTOR",font=("Segoe UI",22,"bold"),text_color="#36e2b4").pack(anchor="w",padx=20,pady=(26,0))
    ctk.CTkLabel(side,text="AI // THREAT-READY LEARNING",font=("Segoe UI",10,"bold"),text_color="#6e93a8").pack(anchor="w",padx=20,pady=(2,18))
    mode_var=ctk.StringVar(value=cfg["mode"]);level_var=ctk.StringVar(value=cfg["level"])
    ctk.CTkLabel(side,text="MODE",text_color="#7f9caf").pack(anchor="w",padx=20,pady=(4,4))
    mode_menu=ctk.CTkOptionMenu(side,values=list(MODES),variable=mode_var,fg_color="#102c3e",button_color="#17445c");mode_menu.pack(fill="x",padx=18)
    ctk.CTkLabel(side,text="LEVEL",text_color="#7f9caf").pack(anchor="w",padx=20,pady=(16,4))
    level_menu=ctk.CTkOptionMenu(side,values=["Beginner","Intermediate","Advanced"],variable=level_var,fg_color="#102c3e",button_color="#17445c");level_menu.pack(fill="x",padx=18)
    provider_lbl=ctk.CTkLabel(side,text=f"ENGINE: {cfg['provider']}",text_color="#36e2b4",font=("Segoe UI",11,"bold"));provider_lbl.pack(anchor="w",padx=20,pady=(22,4))
    status_lbl=ctk.CTkLabel(side,text="Ready",text_color="#7f9caf",wraplength=190,justify="left");status_lbl.pack(anchor="w",padx=20,pady=(0,18))
    settings_btn=ctk.CTkButton(side,text="⚙  Settings",fg_color="#153349",hover_color="#1d4662");settings_btn.pack(fill="x",padx=18,pady=4)
    intel_btn=ctk.CTkButton(side,text="◉  Live Cyber Intel",fg_color="#153349",hover_color="#1d4662");intel_btn.pack(fill="x",padx=18,pady=4)
    clear_btn=ctk.CTkButton(side,text="⌫  Clear Session",fg_color="#182838",hover_color="#293d50");clear_btn.pack(fill="x",padx=18,pady=4)
    copy_btn=ctk.CTkButton(side,text="⧉  Copy Last Answer",fg_color="#182838",hover_color="#293d50");copy_btn.pack(fill="x",padx=18,pady=4)
    export_btn=ctk.CTkButton(side,text="⇩  Export Chat",fg_color="#182838",hover_color="#293d50");export_btn.pack(fill="x",padx=18,pady=4)
    update_btn=ctk.CTkButton(side,text="↻  Check Updates",fg_color="#182838",hover_color="#293d50");update_btn.pack(fill="x",padx=18,pady=4)
    ctk.CTkLabel(side,text=f"Operator: {OWNER_NAME}\\nAuthorized labs • Defensive learning",font=("Segoe UI",10),text_color="#58778b",justify="left").pack(side="bottom",anchor="w",padx=20,pady=20)

    mainf=ctk.CTkFrame(app,fg_color="#06111d",corner_radius=0);mainf.grid(row=0,column=1,sticky="nsew",padx=0,pady=0);mainf.grid_columnconfigure(0,weight=1);mainf.grid_rowconfigure(3,weight=1)
    hero=ctk.CTkFrame(mainf,fg_color="#0b2030",corner_radius=18,border_width=1,border_color="#183b4f");hero.grid(row=0,column=0,sticky="ew",padx=20,pady=(20,10))
    ctk.CTkLabel(hero,text="THINK LIKE AN ANALYST. BUILD LIKE AN ENGINEER.",font=("Segoe UI",20,"bold"),text_color="#f2fbff").pack(anchor="w",padx=18,pady=(16,3))
    ctk.CTkLabel(hero,text=f"Ask one problem. CyberMentor routes the workflow automatically.  •  Built by {OWNER_NAME}",font=("Segoe UI",12),text_color="#7ea0b3").pack(anchor="w",padx=18,pady=(0,14))

    topics=ctk.CTkScrollableFrame(mainf,height=78,orientation="horizontal",fg_color="transparent");topics.grid(row=1,column=0,sticky="ew",padx=18,pady=(0,6))
    topic_buttons=[]
    chat=ctk.CTkTextbox(mainf,wrap="word",font=("Segoe UI",13),fg_color="#081623",border_width=1,border_color="#19384b",corner_radius=16);chat.grid(row=3,column=0,sticky="nsew",padx=20,pady=(6,10))
    if history:
        for role,text in history[-30:]:
            tag="YOU" if role=="user" else "CYBERMENTOR"
            chat.insert("end",f"{tag}\n{text.strip()}\n\n")
    else:
        chat.insert("end","CYBERMENTOR AI // SECURITY OPERATIONS CONSOLE\nDrop a cyber problem, topic, lab, alert, exam goal or project.\n\n")
    chat.configure(state="disabled")
    inputf=ctk.CTkFrame(mainf,fg_color="transparent");inputf.grid(row=4,column=0,sticky="ew",padx=20,pady=(0,20));inputf.grid_columnconfigure(0,weight=1)
    entry=ctk.CTkTextbox(inputf,height=78,wrap="word",fg_color="#0b1e2c",border_width=1,border_color="#22506a",corner_radius=14);entry.grid(row=0,column=0,sticky="ew",padx=(0,10))
    send_btn=ctk.CTkButton(inputf,text="RUN  ▶",width=110,height=48,fg_color="#21c99a",hover_color="#19aa82",text_color="#031611",font=("Segoe UI",13,"bold"));send_btn.grid(row=0,column=1,sticky="ns")

    def append(role,text):
        chat.configure(state="normal")
        tag="YOU" if role=="user" else "CYBERMENTOR"
        chat.insert("end",f"{tag}\n{text.strip()}\n\n")
        chat.configure(state="disabled");chat.see("end")

    def persist_selects(*_):
        cfg["mode"]=mode_var.get();cfg["level"]=level_var.get();save_cfg(cfg)
    mode_var.trace_add("write",persist_selects);level_var.trace_add("write",persist_selects)

    def open_settings():
        win=ctk.CTkToplevel(app);win.title("CyberMentor AI Settings");win.geometry("720x720");win.minsize(650,600);win.transient(app);win.grab_set()
        provider=ctk.StringVar(value=cfg["provider"])
        model=ctk.StringVar(value=cfg.get("model",""))
        model_profile=ctk.StringVar(value=cfg.get("model_profile","Auto Best"))
        language=ctk.StringVar(value=cfg.get("language","Auto"))
        detail=ctk.StringVar(value=cfg.get("detail","Professional"))
        ollama=ctk.StringVar(value=cfg.get("ollama_url","http://127.0.0.1:11434"))
        backend=ctk.StringVar(value=cfg.get("backend_url",""))
        token=ctk.StringVar(value=cfg.get("backend_token",""))
        key=ctk.StringVar(value="")
        key_visible={"show":False}

        body=ctk.CTkScrollableFrame(win,fg_color="transparent");body.pack(fill="both",expand=True,padx=10,pady=10)
        ctk.CTkLabel(body,text="QUICK CONNECT",font=("Segoe UI",22,"bold"),text_color="#36e2b4").pack(anchor="w",padx=12,pady=(10,3))
        ctk.CTkLabel(body,text="Paste your API key once, press SAVE & CONNECT, then just ask questions.",text_color="#839dad").pack(anchor="w",padx=12,pady=(0,14))

        quick=ctk.CTkFrame(body,fg_color="#101d27",corner_radius=14);quick.pack(fill="x",padx=12,pady=(0,12))
        ctk.CTkLabel(quick,text="OpenAI API key",font=("Segoe UI",13,"bold")).pack(anchor="w",padx=14,pady=(14,4))
        key_row=ctk.CTkFrame(quick,fg_color="transparent");key_row.pack(fill="x",padx=14,pady=(0,6));key_row.grid_columnconfigure(0,weight=1)
        key_entry=ctk.CTkEntry(key_row,textvariable=key,show="*",placeholder_text="Paste API key here")
        key_entry.grid(row=0,column=0,sticky="ew")
        show_btn=ctk.CTkButton(key_row,text="SHOW",width=72,fg_color="#183b52");show_btn.grid(row=0,column=1,padx=(8,0))
        key_status=ctk.CTkLabel(quick,text=("Saved key detected on this PC" if get_secret() else "No key saved yet"),text_color=("#36e2b4" if get_secret() else "#839dad"))
        key_status.pack(anchor="w",padx=14,pady=(0,8))
        connect_btn=ctk.CTkButton(quick,text="SAVE & CONNECT",height=46,fg_color="#21c99a",hover_color="#19aa82",text_color="#031611",font=("Segoe UI",13,"bold"))
        connect_btn.pack(fill="x",padx=14,pady=(0,8))
        test_btn=ctk.CTkButton(quick,text="TEST SAVED CONNECTION",height=36,fg_color="#1e725f",hover_color="#23866f")
        test_btn.pack(fill="x",padx=14,pady=(0,8))
        quick_actions=ctk.CTkFrame(quick,fg_color="transparent");quick_actions.pack(fill="x",padx=14,pady=(0,14))
        ctk.CTkButton(quick_actions,text="Get API key",command=lambda:webbrowser.open("https://platform.openai.com/api-keys"),fg_color="#183b52").pack(side="left")
        clear_key_btn=ctk.CTkButton(quick_actions,text="CLEAR SAVED KEY",fg_color="#39232a",hover_color="#532d37");clear_key_btn.pack(side="right")

        prefs=ctk.CTkFrame(body,fg_color="#0d1822",corner_radius=14);prefs.pack(fill="x",padx=12,pady=(0,12))
        ctk.CTkLabel(prefs,text="ASSISTANT PREFERENCES",font=("Segoe UI",13,"bold"),text_color="#cbeef2").pack(anchor="w",padx=14,pady=(14,8))
        ctk.CTkLabel(prefs,text="Model profile").pack(anchor="w",padx=14)
        ctk.CTkOptionMenu(prefs,values=["Auto Best","Balanced","Economy","Cyber Specialized"],variable=model_profile).pack(fill="x",padx=14,pady=(4,10))
        ctk.CTkLabel(prefs,text="Response language").pack(anchor="w",padx=14)
        ctk.CTkOptionMenu(prefs,values=["Auto","English","Hindi","Hinglish"],variable=language).pack(fill="x",padx=14,pady=(4,10))
        ctk.CTkLabel(prefs,text="Answer depth").pack(anchor="w",padx=14)
        ctk.CTkOptionMenu(prefs,values=["Quick","Professional","Deep"],variable=detail).pack(fill="x",padx=14,pady=(4,14))

        advanced=ctk.CTkFrame(body,fg_color="#0d1822",corner_radius=14);advanced.pack(fill="x",padx=12,pady=(0,12))
        ctk.CTkLabel(advanced,text="ADVANCED ENGINE SETTINGS",font=("Segoe UI",13,"bold"),text_color="#cbeef2").pack(anchor="w",padx=14,pady=(14,8))
        ctk.CTkLabel(advanced,text="Provider").pack(anchor="w",padx=14)
        ctk.CTkOptionMenu(advanced,values=["OpenAI","Ollama","Secure Backend"],variable=provider).pack(fill="x",padx=14,pady=(4,10))
        ctk.CTkLabel(advanced,text="Manual model override (optional)").pack(anchor="w",padx=14)
        ctk.CTkEntry(advanced,textvariable=model,placeholder_text="Blank = automatic").pack(fill="x",padx=14,pady=(4,10))
        ctk.CTkLabel(advanced,text="Ollama URL").pack(anchor="w",padx=14)
        ctk.CTkEntry(advanced,textvariable=ollama).pack(fill="x",padx=14,pady=(4,10))
        ctk.CTkLabel(advanced,text="Secure backend HTTPS URL").pack(anchor="w",padx=14)
        ctk.CTkEntry(advanced,textvariable=backend).pack(fill="x",padx=14,pady=(4,10))
        ctk.CTkLabel(advanced,text="Backend access token (optional)").pack(anchor="w",padx=14)
        ctk.CTkEntry(advanced,textvariable=token,show="*").pack(fill="x",padx=14,pady=(4,14))

        msg=ctk.CTkLabel(body,text="",text_color="#e6bf66",wraplength=640,justify="left");msg.pack(anchor="w",padx=12,pady=(6,4))
        save_settings_btn=ctk.CTkButton(body,text="SAVE ALL SETTINGS",height=42,fg_color="#163a4f",hover_color="#1d4c66")
        save_settings_btn.pack(fill="x",padx=12,pady=(6,16))

        def apply_cfg():
            cfg.update(provider=provider.get(),model=model.get().strip(),model_profile=model_profile.get(),language=language.get(),detail=detail.get(),ollama_url=ollama.get().strip(),backend_url=backend.get().strip(),backend_token=token.get().strip())
            save_cfg(cfg);provider_lbl.configure(text=f"ENGINE: {cfg['provider']}");status_lbl.configure(text="Settings saved • ready")
            msg.configure(text="Settings saved.",text_color="#36e2b4")

        def toggle_key():
            key_visible["show"]=not key_visible["show"]
            key_entry.configure(show="" if key_visible["show"] else "*")
            show_btn.configure(text="HIDE" if key_visible["show"] else "SHOW")

        def clear_key():
            if set_secret(""):
                key.set("");key_status.configure(text="Saved API key cleared.",text_color="#839dad");status_lbl.configure(text="OpenAI key not configured")
            else:key_status.configure(text="Could not clear the saved key.",text_color="#ff8c8c")

        def save_and_connect():
            raw=key.get().strip()
            if raw:
                if len(raw)<20:
                    key_status.configure(text="The pasted API key looks incomplete.",text_color="#ffb65c");return
                if not set_secret(raw):
                    key_status.configure(text="Windows could not securely save the key.",text_color="#ff8c8c");return
                key.set("")
            saved=get_secret()
            if not saved:
                key_status.configure(text="Paste your API key, then press SAVE & CONNECT.",text_color="#ffb65c");return
            provider.set("OpenAI");cfg["provider"]="OpenAI";cfg["model_profile"]=model_profile.get();cfg["language"]=language.get();cfg["detail"]=detail.get();save_cfg(cfg)
            key_status.configure(text="API KEY SAVED ✓  Testing connection…",text_color="#e6bf66")
            connect_btn.configure(state="disabled",text="CONNECTING…");test_btn.configure(state="disabled")
            def work():
                try:
                    code,d=req_json("https://api.openai.com/v1/models",headers={"Authorization":"Bearer "+saved},timeout=25)
                    if code>=400:raise RuntimeError(extract_text(d))
                    chosen=model.get().strip() or choose_model([x.get("id") for x in d.get("data",[])],cfg.get("mode","Learning"),model_profile.get())
                    if not chosen:raise RuntimeError("No compatible model was returned by the provider.")
                    cfg.update(provider="OpenAI",model=chosen,model_profile=model_profile.get(),language=language.get(),detail=detail.get());save_cfg(cfg)
                    def ok():
                        model.set(chosen);key_status.configure(text=f"CONNECTED ✓  {chosen}",text_color="#36e2b4")
                        provider_lbl.configure(text="ENGINE: OpenAI");status_lbl.configure(text=f"Ready • {chosen}")
                        connect_btn.configure(state="normal",text="SAVE & CONNECT");test_btn.configure(state="normal")
                        msg.configure(text="Connection verified. Close Settings and press RUN.",text_color="#36e2b4")
                    app.after(0,ok)
                except Exception as e:
                    def bad():
                        key_status.configure(text="Saved, but connection failed: "+friendly_error(e),text_color="#ff8c8c")
                        connect_btn.configure(state="normal",text="SAVE & CONNECT");test_btn.configure(state="normal")
                    app.after(0,bad)
            threading.Thread(target=work,daemon=True).start()

        show_btn.configure(command=toggle_key)
        connect_btn.configure(command=save_and_connect)
        test_btn.configure(command=save_and_connect)
        clear_key_btn.configure(command=clear_key)
        save_settings_btn.configure(command=apply_cfg)
        if not get_secret():win.after(250,key_entry.focus_set)

    def send():
        q=entry.get("1.0","end").strip()
        if not q:return
        cfg["mode"]=mode_var.get();cfg["level"]=level_var.get();save_cfg(cfg)
        if cfg["provider"]=="OpenAI" and not get_secret():
            append("assistant","AI setup required once: open Settings, choose OpenAI and save your API key. Nothing else needs to be installed.")
            open_settings();return
        if cfg["provider"]=="Secure Backend" and not cfg.get("backend_url"):
            append("assistant","Secure Backend is selected but no server address is configured. Open Settings and add the HTTPS backend URL.")
            open_settings();return
        entry.delete("1.0","end");append("user",q);send_btn.configure(state="disabled",text="WORKING…");status_lbl.configure(text="Analyzing your request…")
        payload_history=[{"role":"user" if r=="user" else "assistant","content":t} for r,t in history[-10:]]
        def work():
            try:
                answer=provider_chat(cfg,q,payload_history)
                history.append(("user",q));history.append(("assistant",answer));save_history(history)
                app.after(0,lambda:append("assistant",answer))
                app.after(0,lambda:status_lbl.configure(text=f"Ready • {cfg['provider']} • {cfg.get('model') or 'auto model'}"))
            except Exception as e:
                if str(e)=="SETUP_REQUIRED":
                    msg="AI setup is required once. Open Settings and configure OpenAI, Ollama or a Secure Backend."
                else:msg=friendly_error(e)
                app.after(0,lambda:append("assistant",msg))
                app.after(0,lambda:status_lbl.configure(text="Needs setup • open Settings"))
            finally:
                app.after(0,lambda:send_btn.configure(state="normal",text="RUN  ▶"))
        threading.Thread(target=work,daemon=True).start()

    def choose_topic(t):
        entry.delete("1.0","end");entry.insert("1.0",f"Teach me {t} from my current level with a practical cybersecurity example.")
    for t in TOPICS:
        b=ctk.CTkButton(topics,text=t,width=max(92,len(t)*8+24),height=32,fg_color="#102b3c",hover_color="#174259",corner_radius=16,command=lambda x=t:choose_topic(x))
        b.pack(side="left",padx=4,pady=4);topic_buttons.append(b)

    def clear():
        history.clear();save_history(history);chat.configure(state="normal");chat.delete("1.0","end");chat.insert("end","New CyberMentor session ready.\n\n");chat.configure(state="disabled")
    def copy_last():
        for role,text in reversed(history):
            if role=="assistant":
                app.clipboard_clear();app.clipboard_append(text);status_lbl.configure(text="Last answer copied to clipboard");return
        status_lbl.configure(text="No answer to copy yet")
    def export_chat():
        try:
            from tkinter import filedialog
            path=filedialog.asksaveasfilename(title="Export CyberMentor chat",defaultextension=".txt",filetypes=[("Text file","*.txt"),("JSON file","*.json")])
            if not path:return
            p=Path(path)
            if p.suffix.lower()==".json":
                p.write_text(json.dumps([{"role":r,"text":t} for r,t in history],ensure_ascii=False,indent=2),encoding="utf-8")
            else:
                p.write_text("\n\n".join(("YOU" if r=="user" else "CYBERMENTOR")+"\n"+t for r,t in history),encoding="utf-8")
            status_lbl.configure(text="Chat exported successfully")
        except Exception as e:
            status_lbl.configure(text="Could not export chat")
    def check_updates():
        status_lbl.configure(text="Checking GitHub Releases…")
        def work():
            try:
                _,d=req_json(f"https://api.github.com/repos/{REPO}/releases/latest",timeout=20)
                tag=d.get("tag_name","latest")
                url=d.get("html_url",f"https://github.com/{REPO}/releases/latest")
                app.after(0,lambda:status_lbl.configure(text=f"Latest release: {tag}"))
                app.after(0,lambda:webbrowser.open(url))
            except Exception:
                app.after(0,lambda:status_lbl.configure(text="Could not check updates right now"))
        threading.Thread(target=work,daemon=True).start()
    def intel():
        status_lbl.configure(text="Refreshing CISA/NVD learning feed…")
        def work():
            try:
                _,d=req_json(DEFAULT_FEED,timeout=20);items=d.get("items",[])[:12]
                text="LIVE CYBER INTEL\n\n"+"\n\n".join(f"{x.get('title','Security item')}\n{x.get('source','')} {x.get('date','')}\n{x.get('summary','')[:500]}" for x in items)
                app.after(0,lambda:append("assistant",text or "The feed is currently empty."))
                app.after(0,lambda:status_lbl.configure(text="Intel refreshed"))
            except Exception as e:app.after(0,lambda:append("assistant",friendly_error(e)))
        threading.Thread(target=work,daemon=True).start()
    settings_btn.configure(command=open_settings);intel_btn.configure(command=intel);clear_btn.configure(command=clear);copy_btn.configure(command=copy_last);export_btn.configure(command=export_chat);update_btn.configure(command=check_updates);send_btn.configure(command=send)
    app.bind("<Control-Return>",lambda e:send())
    app.mainloop();return 0

if __name__=="__main__":
    raise SystemExit(main())
