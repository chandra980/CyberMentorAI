#!/usr/bin/env python3
from pathlib import Path
import json, py_compile, sys, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
errors=[]

for p in [ROOT/"backend/server.py",ROOT/"cli/cybermentor.py",ROOT/"desktop/gui.py",ROOT/"scripts/update_cyber_feed.py"]:
    try: py_compile.compile(str(p), doraise=True)
    except Exception as e: errors.append(f"Python compile failed {p}: {e}")

try: json.loads((ROOT/"data/cyber_feed.json").read_text(encoding="utf-8"))
except Exception as e: errors.append(f"JSON invalid: {e}")

for p in [ROOT/"android-app/app/src/main/AndroidManifest.xml", *list((ROOT/"android-app/app/src/main/res").rglob("*.xml"))]:
    try: ET.parse(p)
    except Exception as e: errors.append(f"XML invalid {p}: {e}")

java=(ROOT/"android-app/app/src/main/java/ai/cybermentor/mobile/MainActivity.java").read_text(encoding="utf-8")
html=(ROOT/"android-app/app/src/main/assets/index.html").read_text(encoding="utf-8")
for method in ["chat(","backendChat(","startVoice(","speak(","shareText(","refreshOpenAIModels(","fetchCyberFeed(","checkForUpdates(","openUrl(","openApiKeyPage(","toast("]:
    if method not in java: errors.append(f"Android bridge missing {method}")
for token in ["AndroidAI.chat","AndroidAI.backendChat","AndroidAI.startVoice","AndroidAI.saveApiKey","AndroidAI.refreshOpenAIModels","AndroidAI.fetchCyberFeed","AndroidAI.checkForUpdates"]:
    if token not in html: errors.append(f"Mobile UI missing {token}")
if "\\n        @JavascriptInterface" in java: errors.append("Literal escaped newline found in Java source")


desktop=(ROOT/"desktop/gui.py").read_text(encoding="utf-8")
for token in [
    "SAVE & CONNECT","TEST SAVED CONNECTION","CLEAR SAVED KEY",
    "Copy Last Answer","Export Chat","Check Updates",
    "Auto Best","Balanced","Economy","Cyber Specialized",
    "English","Hindi","Hinglish","Operator:"
]:
    if token not in desktop: errors.append(f"Desktop feature missing: {token}")
for token in [
    "SAVE KEY","AUTO-DETECT MODEL","Auto-routing","Quick topics",
    "AndroidAI.saveApiKey","AndroidAI.checkForUpdates"
]:
    if token not in html: errors.append(f"Android UX feature missing: {token}")

required=[ROOT/".github/workflows/build-apk.yml",ROOT/".github/workflows/build-desktop.yml",ROOT/".github/workflows/publish-release.yml",ROOT/".github/workflows/update-intel.yml"]
for p in required:
    if not p.exists(): errors.append(f"Missing workflow: {p.name}")

if errors:
    print("\n".join("ERROR: "+e for e in errors))
    sys.exit(1)
import subprocess
for cmd in [
    [sys.executable,str(ROOT/"desktop/gui.py"),"--self-test"],
    [sys.executable,str(ROOT/"cli/cybermentor.py"),"--self-test"],
]:
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    if p.returncode!=0: errors.append("Self-test failed: "+" ".join(cmd)+"\n"+p.stdout+"\n"+p.stderr)

if errors:
    print("\n".join("ERROR: "+e for e in errors))
    sys.exit(1)
print("QA checks passed")
