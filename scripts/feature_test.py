#!/usr/bin/env python3
import importlib.util, json, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

gui=load("cybermentor_gui",ROOT/"desktop/gui.py")
backend=load("cybermentor_backend",ROOT/"backend/server.py")

# Auto routing
cases={
    "Investigate suspicious Sysmon alert":"SOC",
    "Create a DVWA practice lab":"Lab",
    "Run a mock SOC analyst interview":"Interview",
    "Make a firewall lesson plan for students":"Teacher",
    "Design a cybersecurity capstone project":"Project",
    "I have a network security MCQ exam":"Exam",
    "Teach me DNS security":"Learning",
}
for prompt,expected in cases.items():
    got=gui.auto_route_mode(prompt)
    assert got==expected,(prompt,got,expected)

# Newest generation selection must not require a hard-coded current version.
models=["gpt-5.6-sol","gpt-6-terra","gpt-7-luna","gpt-7-sol","gpt-7-audio","gpt-7-realtime"]
assert gui.choose_model(models,"Learning","Auto Best")=="gpt-7-sol"
assert backend.choose_openai_model(models)=="gpt-7-sol"

# Specialized models must not become default general-chat models.
mixed=["gpt-7-terra","gpt-9-cyber","gpt-daybreak-red-latest"]
assert gui.choose_model(mixed,"Learning","Auto Best")=="gpt-7-terra"
assert backend.choose_openai_model(mixed)=="gpt-7-terra"

# Cyber-specialized selection is opt-in and mode-specific.
special=gui.choose_model(mixed,"SOC","Cyber Specialized")
assert special in {"gpt-9-cyber","gpt-daybreak-red-latest"}

# Prompt format / preferences
cfg={"language":"Hinglish","detail":"Deep"}
inst=gui.system_instruction("Teacher","Intermediate",cfg)
for token in ["Teacher","Intermediate","Hinglish","Deep","KEY TAKEAWAY"]:
    assert token in inst,token

# Config/history round trip in an isolated temp directory.
with tempfile.TemporaryDirectory() as td:
    gui.CONFIG_DIR=Path(td)
    gui.CONFIG_FILE=Path(td)/"config.json"
    gui.HISTORY_FILE=Path(td)/"history.json"
    cfg=gui.load_cfg()
    cfg.update(provider="OpenAI",mode="Auto",language="Hindi",detail="Professional")
    gui.save_cfg(cfg)
    loaded=gui.load_cfg()
    assert loaded["provider"]=="OpenAI"
    assert loaded["language"]=="Hindi"
    history=[("user","hello"),("assistant","hi")]
    gui.save_history(history)
    assert gui.load_history()==history

# Backend response normalization
n=backend.normalized("ok","test-model","test-provider")
assert n["output"][0]["content"][0]["text"]=="ok"
assert n["model"]=="test-model"

print("Feature tests passed")
