# CyberMentor AI - Installation and Usage

This guide is written for people who receive only the repository link and want the easiest path for their platform.

## 1. Android phone or tablet

Open the latest release page:

https://github.com/chandra980/CyberMentorAI/releases/latest

Download:

`CyberMentorAI-Android.apk`

Then:

1. Open the downloaded APK.
2. If Android blocks installation, allow **Install unknown apps** for the browser or file manager you used.
3. Install and open **CyberMentor AI**.
4. Open **Settings** inside the app.
5. For personal use choose **Direct OpenAI**, add your own API key, press **Save key**, then **Refresh models**.
6. For a shared/production setup choose **Secure backend** and enter the HTTPS backend URL supplied by the server owner.
7. Choose Learning, Lab, SOC, Pentest, Exam, Interview, Teacher or Project mode.

Direct APK link after a release exists:

https://github.com/chandra980/CyberMentorAI/releases/latest/download/CyberMentorAI-Android.apk

## 2. Windows

From the same Releases page download:

- `CyberMentorAI-Windows.exe` - GUI
- `cybermentor-Windows.exe` - CLI
- `cybermentor-backend-Windows.exe` - local backend

### Simple OpenAI setup

Open PowerShell:

```powershell
$env:AI_PROVIDER="openai"
$env:OPENAI_API_KEY="YOUR_KEY"
.\cybermentor-backend-Windows.exe
```

Keep that window open. Then launch `CyberMentorAI-Windows.exe`.

### Local/free Ollama setup

Install Ollama separately, download a model, then:

```powershell
$env:AI_PROVIDER="ollama"
$env:OLLAMA_MODEL="YOUR_INSTALLED_MODEL"
.\cybermentor-backend-Windows.exe
```

Then open the GUI or CLI.

## 3. macOS

Download:

- `CyberMentorAI-macOS`
- `cybermentor-macOS`
- `cybermentor-backend-macOS`

In Terminal:

```bash
chmod +x CyberMentorAI-macOS cybermentor-macOS cybermentor-backend-macOS
export AI_PROVIDER=openai
export OPENAI_API_KEY='YOUR_KEY'
./cybermentor-backend-macOS
```

Then launch the GUI binary from another Terminal window.

macOS Gatekeeper may require the user to approve an unsigned community binary in Privacy & Security.

## 4. Linux

Download:

- `CyberMentorAI-Linux`
- `cybermentor-Linux`
- `cybermentor-backend-Linux`

Run:

```bash
chmod +x CyberMentorAI-Linux cybermentor-Linux cybermentor-backend-Linux
export AI_PROVIDER=openai
export OPENAI_API_KEY='YOUR_KEY'
./cybermentor-backend-Linux
```

Then start `./CyberMentorAI-Linux`.

If Tk is not available on the Linux desktop, install the distribution's Tk package or use the CLI.

## 5. CLI

With the backend running:

```bash
./cybermentor-Linux --once "Explain DNS security"
```

or on Windows:

```powershell
.\cybermentor-Windows.exe --once "Explain DNS security"
```

Interactive mode starts when `--once` is omitted.

## 6. Source-code users

Python 3.12+:

```bash
python backend/server.py
python desktop/gui.py
python cli/cybermentor.py
```

Android developers can open `android-app/` in Android Studio or use the GitHub Actions build.

## 7. Internet-updated cybersecurity topics

The repository runs a scheduled workflow that refreshes defensive metadata from CISA KEV and NIST NVD into:

`data/cyber_feed.json`

The Android Intel screen can read this feed. The updater is defensive and does not download or execute exploit code.

## 8. Updates

The Android app checks GitHub Releases for new versions. It cannot silently install an update; Android requires user approval.

Desktop users should download the newer binary from Releases.

## 9. Important security note

Do not commit a personal or shared OpenAI API key into this public repository. For public distribution, keep provider secrets on a backend server and expose only an authenticated HTTPS endpoint to clients.

## 10. Troubleshooting

**404 on the direct APK link:** no successful GitHub Release exists yet, or the asset name differs. Open the Releases page and confirm the asset is present.

**Android app says no API key:** Settings -> Direct OpenAI -> save your key -> refresh models.

**Backend mode fails:** confirm the backend URL uses HTTPS (except localhost), the server is running, and the access token matches.

**Desktop GUI cannot connect:** start the backend first or set `CYBERMENTOR_BACKEND` to the correct URL.

**Ollama model not found:** install the model in Ollama and set `OLLAMA_MODEL` to that exact installed model name.
