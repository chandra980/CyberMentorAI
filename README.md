# CyberMentor AI

## Start here

For platform-by-platform installation and usage, read **[INSTALL.md](INSTALL.md)**.

Quick links:

- Repository: https://github.com/chandra980/CyberMentorAI
- Actions: https://github.com/chandra980/CyberMentorAI/actions
- Releases: https://github.com/chandra980/CyberMentorAI/releases/latest
- Android direct APK (after a successful release): https://github.com/chandra980/CyberMentorAI/releases/latest/download/CyberMentorAI-Android.apk


Advanced multiplatform cybersecurity learning assistant for Android, Windows, macOS, Linux, CLI and browser-connected workflows. Desktop v3 runs standalone with direct OpenAI, Ollama, or Secure Backend modes; a separate backend is optional.

Built around the case-study design loop:

**Problem -> User -> Role -> Instructions -> Context / Knowledge -> Output -> Test -> Find Failure -> Refine -> Retest**

## Download

Recommended Windows installer after the next v3 release:

`CyberMentorAI-Setup-Windows.exe`


After the first successful release build:

- Latest release page: https://github.com/chandra980/CyberMentorAI/releases/latest
- Direct Android APK: https://github.com/chandra980/CyberMentorAI/releases/latest/download/CyberMentorAI-Android.apk

> Android will still ask the user to approve installation of an APK downloaded outside Google Play.

## Included targets

| Target | Implementation |
|---|---|
| Android | Native Java shell + secure WebView bridge |
| Windows/macOS/Linux GUI | Python + Tkinter, packaged with PyInstaller |
| CLI | Python client |
| Backend | Python API gateway |
| Web | Lightweight browser companion |
| Current cyber topics | Scheduled CISA KEV + NIST NVD refresh |

## Core assistant modes

- Learning
- Authorized Lab
- SOC Analyst
- Pentest Learning
- Exam Coach
- Interview Coach
- Teacher
- Project

The assistant adapts to Beginner, Intermediate and Advanced levels.

## AI providers

### OpenAI

For personal use, the Android app can store a user's own API key using Android Keystore encryption.

For a shared/public build, use the backend architecture so a shared provider key is never embedded in the APK, EXE, JavaScript bundle or repository.

The app can query the provider's model endpoint so the selectable model list can be refreshed instead of permanently depending on one hard-coded catalog.

### Ollama / local models

The backend also supports a local Ollama server:

```bash
export AI_PROVIDER=ollama
export OLLAMA_MODEL=qwen3:8b
python backend/server.py
```

Local models avoid per-request cloud API charges but require suitable hardware.

### OpenAI-compatible endpoint

Configure:

```bash
export AI_PROVIDER=compatible
export COMPAT_BASE_URL=https://your-provider.example
export COMPAT_API_KEY=...
```

## Backend with OpenAI

```bash
export AI_PROVIDER=openai
export OPENAI_API_KEY=your-key
export OPENAI_MODEL=your-model-id
python backend/server.py
```

If exposing the backend to other devices, set an application token and put the service behind HTTPS:

```bash
export HOST=0.0.0.0
export APP_ACCESS_TOKEN=a-long-random-secret
python backend/server.py
```

## CLI

```bash
python cli/cybermentor.py --once "Explain Kerberos for a SOC analyst"
```

Interactive:

```bash
python cli/cybermentor.py
```

## Desktop GUI

The packaged GUI is standalone for normal personal use. Open **Settings** once and choose OpenAI, Ollama, or Secure Backend. No separate CyberMentor backend process is required unless you specifically want shared/server mode.

Source run:

```bash
python desktop/gui.py
```

## Android

The Android app includes:

- mobile-first chat UI
- Learning/Lab/SOC/Pentest/Exam/Interview/Teacher/Project modes
- level control
- local chat history
- voice input and text-to-speech
- encrypted personal API-key storage
- secure backend mode
- live model refresh
- cybersecurity intelligence feed
- GitHub Release update checks
- app icon and splash screen

## Automatic internet updates

A scheduled GitHub Action refreshes defensive security topics from:

- CISA Known Exploited Vulnerabilities
- NIST National Vulnerability Database

The updater stores metadata in `data/cyber_feed.json`. It does not fetch or execute exploit code.

## GitHub Actions and QA

- **Build Android APK** - test APK on Android-related pushes or manual run.
- **Build Desktop and CLI** - Windows/Linux/macOS packages.
- **Update Cybersecurity Intelligence** - daily defensive-topic refresh.
- **Publish Installers** - automatically builds and publishes a GitHub Release with Android APK, desktop GUI, CLI and backend binaries when application code changes.
- **Cross-platform QA** - validates Python syntax, Android XML, mobile bridge consistency, mobile JavaScript syntax and backend health on every push.

## Security boundary

CyberMentor AI is for education, defensive security and authorized testing. Practical lab work should target systems you own, have explicit permission to test, or intentionally vulnerable training environments.

## Repository owner

Maintained under: **chandra980/CyberMentorAI**
