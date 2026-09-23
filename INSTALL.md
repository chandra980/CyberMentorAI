# CyberMentor AI — Installation

This repository keeps a **single current supported release**. Use the latest release page instead of choosing an old version:

https://github.com/chandra980/CyberMentorAI/releases/latest

## Windows — recommended

Download:

`CyberMentorAI-Setup-Windows.exe`

Then:

1. Open the installer.
2. Install CyberMentor AI.
3. Launch the app.
4. Open **Settings**.
5. Provider: **OpenAI**.
6. Paste your API key.
7. Press **SAVE & CONNECT**.
8. Wait for **CONNECTED ✓**.
9. Close Settings.
10. Type your problem and press **RUN**.

You do **not** need to separately start `cybermentor-backend-Windows.exe` for normal personal use.

The portable `CyberMentorAI-Windows.exe` can also be used without the installer.

## Android

Download:

`CyberMentorAI-Android.apk`

Then:

1. Open the APK.
2. Android may ask permission to install apps from that browser/file manager because the APK is distributed outside Google Play.
3. Install and launch **CyberMentor AI**.
4. Open **Settings**.
5. Paste your OpenAI API key.
6. Press **SAVE & CONNECT**.
7. Wait for **CONNECTED ✓**.
8. Ask your question.

The API key is encrypted using Android Keystore.

## API setup

The easiest personal setup is:

```text
CyberMentor AI
    |
    | your own API key stored locally
    v
OpenAI API
```

The app can auto-detect a compatible current model when the model field is left blank.

Do not paste your private API key into GitHub issues, repository files, screenshots, or public chats.

## Local/free Ollama mode

If Ollama is already installed with a local model:

1. Open CyberMentor settings.
2. Provider: **Ollama**.
3. Keep the default local URL unless your Ollama server uses another address.
4. Leave model blank to use the first installed model, or enter an installed model name.
5. Save settings.
6. Ask a question.

Ollama itself and the model must be installed separately because they are independent software and can be several gigabytes.

## Secure Backend mode

This is for an organization or shared deployment.

1. Provider: **Secure Backend**.
2. Enter the HTTPS CyberMentor backend URL.
3. Add an access token if the server owner configured one.
4. Save settings.

A public APK/EXE should never contain a shared master API key.

## Linux

Download `CyberMentorAI-Linux`.

```bash
chmod +x CyberMentorAI-Linux
./CyberMentorAI-Linux
```

Then use Settings exactly as on Windows.

## macOS

Download `CyberMentorAI-macOS`.

```bash
chmod +x CyberMentorAI-macOS
./CyberMentorAI-macOS
```

macOS may require approval in Privacy & Security for an unsigned/non-notarized community binary.

## CLI

OpenAI:

```bash
cybermentor-Windows.exe --provider openai --api-key YOUR_KEY --once "Explain Kerberos"
```

or set `OPENAI_API_KEY` and omit `--api-key`.

Ollama:

```bash
./cybermentor-Linux --provider ollama --once "Teach me Wireshark filters"
```

## What happens after setup

Users can simply type requests such as:

- `Explain DNS security from zero`
- `Give me a SOC alert investigation exercise`
- `Create a DVWA SQL injection training lab`
- `Take my SOC analyst interview`
- `Prepare me for a network security exam`
- `Make a university lesson plan on firewalls`
- `Design an intermediate cybersecurity project`

Auto Mode routes the request to the relevant workflow.

## Updates

Use **Check Updates** inside the desktop app or the Android Settings screen.

Latest release:

https://github.com/chandra980/CyberMentorAI/releases/latest

When a new successful release is published, the release workflow removes older CyberMentor GitHub Releases/tags so users see one supported version.

## Microsoft SmartScreen / browser warnings

A GitHub-hosted executable can still be flagged as an **unrecognized app** or uncommon download by Microsoft Defender SmartScreen even when it contains no malicious code. That reputation decision is made by Microsoft.

The correct production solution is a trusted Windows code-signing certificate and, for maximum distribution trust, a recognized store/distribution channel. Application code must not bypass or disable SmartScreen.

## Android Play Protect / unknown-source prompts

Android can warn when an APK is installed outside Google Play. The app cannot legitimately suppress that Android security prompt.

For strongest production trust, publish a stable release-signed APK/AAB through a recognized Android distribution channel.

## Troubleshooting

**API key saved but connection fails:** press **TEST SAVED CONNECTION** on desktop or **TEST / DETECT MODEL** on Android. A bad key, disabled API billing, unavailable model, or provider/network issue will be shown as a friendly status.

**No model selected:** leave the model field blank and reconnect; CyberMentor will query the available model list.

**Ollama unavailable:** start Ollama and install at least one model.

**Secure backend unavailable:** verify the HTTPS URL and access token.

**Old version still installed:** uninstall the old CyberMentor build, then install the latest supported release from the Releases page.

## Security note

CyberMentor is for defensive security, education, and authorized lab/pentest use only.
