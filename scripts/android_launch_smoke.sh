#!/usr/bin/env bash
set -euo pipefail

API_LEVEL="${1:-unknown}"
APK_PATH="${2:-CyberMentorAI-compat.apk}"
PKG="ai.cybermentor.mobile"
ACTIVITY="$PKG/.MainActivity"

adb wait-for-device
adb install -r "$APK_PATH"
adb shell pm clear "$PKG" >/dev/null || true
adb logcat -c

launch_and_wait() {
  local round="$1"
  adb shell am force-stop "$PKG"
  adb shell am start -W -n "$ACTIVITY"

  local ready=0
  for _ in $(seq 1 40); do
    PID="$(adb shell pidof "$PKG" | tr -d '\r' || true)"
    if [ -z "$PID" ]; then
      echo "CyberMentor process died after launch on API $API_LEVEL (round $round)"
      adb logcat -d
      exit 1
    fi

    if adb shell dumpsys activity activities | grep -F "$PKG/.MainActivity" >/dev/null 2>&1; then
      LOG="$(adb logcat -d -s CyberMentorAI:I '*:S' || true)"
      if printf '%s\n' "$LOG" | grep -F "UI_READY" >/dev/null 2>&1; then
        ready=1
        break
      fi
    fi
    sleep 1
  done

  if [ "$ready" -ne 1 ]; then
    echo "CyberMentor UI did not become ready on API $API_LEVEL (round $round)"
    adb logcat -d
    exit 1
  fi

  LOG_FILE="/tmp/cybermentor-logcat-$API_LEVEL-round-$round.txt"
  adb logcat -d > "$LOG_FILE"
  if grep -A15 "FATAL EXCEPTION" "$LOG_FILE" | grep -F "$PKG" >/dev/null 2>&1; then
    echo "Fatal exception detected on API $API_LEVEL (round $round)"
    cat "$LOG_FILE"
    exit 1
  fi

  echo "CyberMentor launch stable on API $API_LEVEL (round $round), pid=$PID"
}

# Cold start plus repeated relaunches catch lifecycle/WebView regressions.
launch_and_wait 1
launch_and_wait 2
launch_and_wait 3

# Background/foreground lifecycle check.
adb shell input keyevent KEYCODE_HOME
sleep 2
adb shell am start -W -n "$ACTIVITY"
sleep 2
PID="$(adb shell pidof "$PKG" | tr -d '\r' || true)"
if [ -z "$PID" ]; then
  echo "CyberMentor died during background/foreground test on API $API_LEVEL"
  adb logcat -d
  exit 1
fi
if ! adb shell dumpsys activity activities | grep -F "$PKG/.MainActivity" >/dev/null 2>&1; then
  echo "CyberMentor activity was not restored on API $API_LEVEL"
  adb logcat -d
  exit 1
fi

echo "CyberMentor Android API $API_LEVEL lifecycle smoke test passed"
