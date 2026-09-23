#!/usr/bin/env python3
import json,os,threading,urllib.request,tkinter as tk
from tkinter import ttk,scrolledtext
BACKEND=os.getenv("CYBERMENTOR_BACKEND","http://127.0.0.1:8787")
TOKEN=os.getenv("CYBERMENTOR_TOKEN","")
root=tk.Tk();root.title("CyberMentor AI");root.geometry("920x680")
top=ttk.Frame(root,padding=8);top.pack(fill="x")
ttk.Label(top,text="Mode").pack(side="left");mode=ttk.Combobox(top,values=["Learning","Lab","SOC","Pentest","Exam","Interview","Teacher","Project"],width=12);mode.set("Learning");mode.pack(side="left",padx=5)
ttk.Label(top,text="Level").pack(side="left");level=ttk.Combobox(top,values=["Beginner","Intermediate","Advanced"],width=12);level.set("Intermediate");level.pack(side="left",padx=5)
out=scrolledtext.ScrolledText(root,wrap="word",font=("Segoe UI",11));out.pack(fill="both",expand=True,padx=8,pady=8)
bottom=ttk.Frame(root,padding=8);bottom.pack(fill="x");entry=ttk.Entry(bottom);entry.pack(side="left",fill="x",expand=True)
def send():
    q=entry.get().strip()
    if not q:return
    entry.delete(0,"end");out.insert("end","\nYou: "+q+"\n")
    def work():
        try:
            p={"instructions":f"Mode: {mode.get()}. Level: {level.get()}.","input":[{"role":"user","content":q}]}
            h={"Content-Type":"application/json"}
            if TOKEN:h["Authorization"]="Bearer "+TOKEN
            r=urllib.request.Request(BACKEND.rstrip("/")+"/api/chat",data=json.dumps(p).encode(),headers=h,method="POST")
            d=json.loads(urllib.request.urlopen(r,timeout=180).read())
            t=""; 
            for i in d.get("output",[]):
                for c in i.get("content",[]):
                    if c.get("text"):t+=c["text"]
            root.after(0,lambda:out.insert("end","\nCyberMentor: "+(t or json.dumps(d,indent=2))+"\n"))
        except Exception as e:root.after(0,lambda:out.insert("end","\nError: "+str(e)+"\n"))
    threading.Thread(target=work,daemon=True).start()
ttk.Button(bottom,text="Send",command=send).pack(side="left",padx=6);entry.bind("<Return>",lambda e:send())
out.insert("end","CyberMentor AI Desktop GUI\nStart backend/server.py first, or set CYBERMENTOR_BACKEND.")
root.mainloop()
