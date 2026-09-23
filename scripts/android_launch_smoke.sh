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

# Verify the WebView actually rendered the app, not merely that the process stayed alive.
adb shell uiautomator dump /sdcard/cybermentor-window.xml >/dev/null 2>&1 || true
adb pull /sdcard/cybermentor-window.xml /tmp/cybermentor-window.xml >/dev/null 2>&1 || true
if [ -s /tmp/cybermentor-window.xml ]; then
  if ! grep -q "CyberMentor" /tmp/cybermentor-window.xml; then
    echo "CyberMentor UI text not visible in accessibility dump on API $API_LEVEL"
    cat /tmp/cybermentor-window.xml
    adb logcat -d
    exit 1
  fi
fi

LOG="$(adb logcat -d)"
if printf '%s\n' "$LOG" | grep -A8 "FATAL EXCEPTION" | grep -q "$PKG"; then
  echo "Fatal exception detected on API $API_LEVEL"
  printf '%s\n' "$LOG"
  exit 1
fi

echo "CyberMentor launch stable on API $API_LEVEL, pid=$PID"
