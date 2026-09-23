#!/usr/bin/env sh
set -eu
if ! command -v gradle >/dev/null 2>&1; then
  echo "Gradle is not installed. Open this project in Android Studio or use the included GitHub Actions workflow."
  exit 1
fi
: "${ANDROID_HOME:?ANDROID_HOME must point to an Android SDK containing platform 36 and build-tools 36.1.0}"
gradle :app:assembleDebug
printf '\nAPK: app/build/outputs/apk/debug/app-debug.apk\n'
