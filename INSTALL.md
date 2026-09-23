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

From the latest Releases page download:

- `CyberMentorAI-Windows.exe` - recommended GUI
- `cybermentor-Windows.exe` - CLI
- `cybermentor-backend-Windows.exe` - optional shared/local backend

### Easiest Windows use

1. Double-click `CyberMentorAI-Windows.exe`.
2. Open **Settings** once.
3. Choose **OpenAI** and paste your own API key, or choose **Ollama** if you already run a local model, or choose **Secure Backend** if an organization gives you a server URL.
4. Save.
5. Type your problem and press **RUN**.

The Windows GUI no longer requires the separate backend executable for normal personal use. Its Python/runtime GUI dependencies are bundled inside the EXE.

### Local/free Ollama mode

Install Ollama separately and install a model. Then select **Ollama** in CyberMentor settings. No separate CyberMentor backend is required for this personal-local mode.

## 3. macOS

Download `CyberMentorAI-macOS`. Make it executable if required and launch it.

The GUI can connect directly to OpenAI, Ollama, or a Secure Backend. A separate CyberMentor backend is optional.

macOS Gatekeeper may require approval in Privacy & Security because community GitHub binaries are not Apple-notarized.

## 4. Linux

Download `CyberMentorAI-Linux`.

Run:

```bash
chmod +x CyberMentorAI-Linux
./CyberMentorAI-Linux
```

Open Settings once and choose OpenAI, Ollama, or Secure Backend.

If the desktop environment has no graphical display/Tk support, use the CLI instead.

## 5. CLI

The CLI now works directly with OpenAI, Ollama, or an optional backend.

OpenAI:

```bash
cybermentor-Windows.exe --provider openai --api-key YOUR_KEY --once "Explain DNS security"
```

Linux/macOS:

```bash
./cybermentor-Linux --provider openai --once "Explain DNS security"
```

with `OPENAI_API_KEY` set in the environment.

Ollama:

```bash
./cybermentor-Linux --provider ollama --once "Teach me Wireshark filters"
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

**Desktop GUI asks for setup:** open Settings once and choose OpenAI, Ollama, or Secure Backend. The separate backend executable is optional for normal personal use.

**Ollama model not found:** install the model in Ollama and set `OLLAMA_MODEL` to that exact installed model name.
