#!/usr/bin/env bash
# Build Backcountry Hunter APK from the single-file web app.
set -euo pipefail
cd "$(dirname "$0")"

export JAVA_HOME=/home/adbautista/toolchain/jdk-17.0.13+11
export ANDROID_HOME=/home/adbautista/toolchain/sdk
export BT="$ANDROID_HOME/build-tools/34.0.0"
export AJ="$ANDROID_HOME/platforms/android-34/android.jar"
export PATH="$JAVA_HOME/bin:$BT:$PATH"
TAILWIND=/home/adbautista/toolchain/tailwindcss

echo ">> 1/8 generating offline asset"
python3 prepare_asset.py

echo ">> 2/8 compiling tailwind css"
"$TAILWIND" -c tailwind.config.js -i input.css -o app/src/main/assets/tailwind.css --minify

echo ">> 3/8 compiling resources"
rm -rf build && mkdir -p build/classes build/dex
aapt2 compile --dir app/src/main/res -o build/res.zip

echo ">> 4/8 linking resources + assets"
aapt2 link -o build/base.apk -I "$AJ" --manifest app/src/main/AndroidManifest.xml \
  -R build/res.zip -A app/src/main/assets \
  --min-sdk-version 24 --target-sdk-version 34 --version-code 1 --version-name 1.0 \
  --auto-add-overlay

echo ">> 5/8 compiling java"
javac -source 8 -target 8 -bootclasspath "$AJ" -cp "$AJ" -d build/classes \
  app/src/main/java/com/backcountry/hunter/MainActivity.java 2>/dev/null || true
[ -f build/classes/com/backcountry/hunter/MainActivity.class ] || { echo "javac failed"; exit 1; }

echo ">> 6/8 dexing"
d8 --lib "$AJ" --min-api 24 --output build/dex $(find build/classes -name '*.class')

echo ">> 7/8 packaging dex + zipalign"
python3 - <<'PY'
import zipfile
zin = zipfile.ZipFile("build/base.apk")
zout = zipfile.ZipFile("build/withdex.apk", "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    zout.writestr(item, zin.read(item.filename))
zout.writestr("classes.dex", open("build/dex/classes.dex", "rb").read(), zipfile.ZIP_STORED)
zout.close(); zin.close()
PY
zipalign -f -p 4 build/withdex.apk build/aligned.apk

echo ">> 8/8 signing"
[ -f build/debug.keystore ] || keytool -genkeypair -v -keystore build/debug.keystore \
  -storepass android -keypass android -alias androiddebugkey \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Android Debug,O=Backcountry,C=US" >/dev/null 2>&1
apksigner sign --ks build/debug.keystore --ks-pass pass:android --key-pass pass:android \
  --ks-key-alias androiddebugkey --out BackcountryHunter.apk build/aligned.apk
apksigner verify BackcountryHunter.apk && echo "APK OK -> $(pwd)/BackcountryHunter.apk"
