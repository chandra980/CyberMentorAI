#!/usr/bin/env bash
set -euo pipefail

API_LEVEL="${1:-unknown}"
APK_PATH="${2:-CyberMentorAI-compat.apk}"
PKG="ai.cybermentor.mobile"
ACTIVITY="$PKG/.MainActivity"

adb wait-for-device
adb install -r "$APK_PATH"
adb logcat -c
adb shell am force-stop "$PKG"
adb shell am start -W -n "$ACTIVITY"
sleep 8

PID="$(adb shell pidof "$PKG" | tr -d '\r' || true)"
if [ -z "$PID" ]; then
  echo "CyberMentor process died after launch on API $API_LEVEL"
  adb logcat -d
  exit 1
fi

adb shell dumpsys activity activities | grep -q "$PKG/.MainActivity"

# Verify native WebView load and JavaScript initialization.
LOG="$(adb logcat -d)"
if ! printf '%s\n' "$LOG" | grep -q "CyberMentorAI.*WEBAPP_READY"; then
  echo "CyberMentor WebView did not finish loading on API $API_LEVEL"
  printf '%s\n' "$LOG"
  exit 1
fi
if ! printf '%s\n' "$LOG" | grep -q "CyberMentorAI.*UI_READY"; then
  echo "CyberMentor JavaScript UI did not initialize on API $API_LEVEL"
  printf '%s\n' "$LOG"
  exit 1
fi
if printf '%s\n' "$LOG" | grep -A8 "FATAL EXCEPTION" | grep -q "$PKG"; then
  echo "Fatal exception detected on API $API_LEVEL"
  printf '%s\n' "$LOG"
  exit 1
fi

echo "CyberMentor launch stable on API $API_LEVEL, pid=$PID"
