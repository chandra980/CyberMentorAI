# CyberMentor AI

**Professional cybersecurity learning, SOC, lab, exam and project assistant by Chandra Kumar Yadav.**

> **Current-release policy:** this repository publishes one supported release at a time. When a new successful release is published, older GitHub Releases/tags are removed automatically so users are not forced to choose between old versions.

## Download

**Latest supported release:**  
https://github.com/chandra980/CyberMentorAI/releases/latest

Recommended files:

- **Windows:** `CyberMentorAI-Setup-Windows.exe`
- **Android:** `CyberMentorAI-Android.apk`
- **Windows portable:** `CyberMentorAI-Windows.exe`
- **Linux:** `CyberMentorAI-Linux`
- **macOS:** `CyberMentorAI-macOS`
- **CLI:** `cybermentor-<platform>`
- **Optional shared backend:** `cybermentor-backend-<platform>`

## 30-second setup

### Windows

1. Install `CyberMentorAI-Setup-Windows.exe`.
2. Open **CyberMentor AI**.
3. Open **Settings**.
4. Paste your own OpenAI API key.
5. Press **SAVE & CONNECT**.
6. Wait for **CONNECTED ✓**.
7. Type any problem and press **RUN**.

The normal desktop app is standalone. The separate backend executable is optional.

### Android

1. Install `CyberMentorAI-Android.apk`.
2. Open **Settings**.
3. Paste the API key.
4. Press **SAVE & CONNECT**.
5. Wait for **CONNECTED ✓**.
6. Ask your question.

The API key is stored with Android Keystore on Android and the OS credential store/keyring on desktop.

## Core experience

CyberMentor can automatically route a natural-language request into:

- Learning
- Authorized Lab
- SOC Analyst
- Pentest Learning
- Exam Coach
- Interview Coach
- Teacher
- Project

Levels: **Beginner / Intermediate / Advanced**.

Quick topics include networking, OSI/TCP-IP, Linux, Windows, cryptography, web security, OWASP, SOC, SIEM, EDR, IDS/IPS, threat intelligence, incident response, digital forensics, Active Directory, Python, PowerShell, SQL, API security, containers, threat hunting, MITRE ATT&CK, Wireshark, Nmap, Burp Suite, Zeek, Suricata, Splunk, Sysmon, Volatility, YARA and Sigma.

## AI engine

CyberMentor does not require the user to manually track changing model IDs. When the model field is blank, the app queries the provider's available model catalog and selects a compatible current GPT generation automatically.

Desktop preferences include:

- Auto Best / Balanced / Economy / Cyber Specialized model profile
- Auto / English / Hindi / Hinglish language
- Quick / Professional / Deep answer depth
- OpenAI / Ollama / Secure Backend
- manual model override for advanced users

Specialized cyber models are used only when they are actually available to the user's API account and explicitly selected.

## Useful daily features

- persistent local conversation history
- Copy Last Answer
- Export Chat
- Check Updates
- Live Cyber Intel
- CISA KEV + NIST NVD defensive feed
- voice input on Android
- model auto-detection
- friendly error recovery instead of raw Python/network tracebacks
- SHA-256 release checksums
- one-click Windows installer

## Free/local mode

CyberMentor can connect to a locally installed Ollama model. Local model software and model files must already be installed on that computer. No cloud API charge is incurred by CyberMentor for local inference.

## Security architecture

For personal desktop/mobile use, a user may save their own API key locally.

For public or organizational deployments, use:

```text
CyberMentor App
      |
      v
Authenticated HTTPS Backend
      |
      v
AI Provider
```

Never commit a shared provider API key to this public repository.

## Current cyber intelligence

The scheduled updater refreshes defensive metadata from:

- CISA Known Exploited Vulnerabilities
- NIST National Vulnerability Database

It does not download or execute exploit code.

## Quality gates

Every change is checked by automated workflows covering:

- Python compilation
- desktop self-tests
- CLI self-tests
- Android XML validation
- Android native/JavaScript bridge checks
- mobile JavaScript syntax
- backend health smoke test
- Android APK compilation
- Windows/Linux/macOS packaging
- Windows installer generation
- release checksums

See: https://github.com/chandra980/CyberMentorAI/actions

## Installation details

Read **[INSTALL.md](INSTALL.md)** for platform-specific instructions and troubleshooting.

## Platform trust / signing

The project supports normal GitHub distribution, but operating-system reputation warnings are controlled by Microsoft/Google/Apple, not by application UI code. For the strongest production trust, releases should be signed with a stable Android release keystore and a trusted Windows code-signing certificate (and Apple signing/notarization for macOS). The build pipeline can be extended with those private signing credentials without putting them in this public repository.

## Authorized-use boundary

CyberMentor AI is designed for cybersecurity education, defensive security and testing on systems the user owns, has explicit authorization to test, or intentionally vulnerable training labs.
