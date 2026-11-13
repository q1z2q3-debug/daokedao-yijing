#!/usr/bin/env bash
# 把《润泽说 道可道之易传》v1.50.0 阅读页打成离线 APK。
#
# 产物：apk-yijing/dist/道可道-易传-1.50.0.apk
#
# 依赖（可用环境变量覆盖）：
#   SDK        解开的 Android SDK 片段目录，默认 /tmp/apkbuild
#   BUILD_TOOLS  build-tools 目录（需含 aapt2 / d8 / zipalign / apksigner）
#   ANDROID_JAR  android.jar
#   JAVA_HOME   JDK（需含 javac / keytool）
# 签名密钥不放仓库：默认 ~/.daokedao-vault/apk-signing.jks，口令同目录 apk-signing.pass
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd)

SDK=${SDK:-/tmp/apkbuild}
BT=${BUILD_TOOLS:-$SDK/android-14}
AJAR=${ANDROID_JAR:-$SDK/android-35/android.jar}
if [ -z "${JAVA_HOME:-}" ]; then
  JAVA_HOME=$(ls -d "$SDK"/jdk-11* 2>/dev/null | head -1)
fi

VAULT=${VAULT:-$HOME/.daokedao-vault}
KS="$VAULT/apk-signing.jks"
KP="$VAULT/apk-signing.pass"
VERNAME=1.50.0
VERCODE=15000

echo "== 1/6 资源编译 =="
rm -rf build dist && mkdir -p build/gen build/classes build/dex dist
"$BT/aapt2" compile --dir res -o build/res.zip

echo "== 2/6 资源链接 =="
"$BT/aapt2" link -o build/base.apk \
  -I "$AJAR" \
  --manifest AndroidManifest.xml \
  -A assets \
  --java build/gen \
  -R build/res.zip \
  --auto-add-overlay \
  --target-sdk-version 34 \
  --version-code "$VERCODE" --version-name "$VERNAME"

echo "== 3/6 编译 java =="
"$JAVA_HOME/bin/javac" -encoding UTF-8 -source 8 -target 8 \
  -bootclasspath "$AJAR" -classpath "$AJAR" \
  -d build/classes \
  build/gen/com/daokedao/yijing/R.java \
  java/com/daokedao/yijing/MainActivity.java 2>&1 | grep -v "^警告\|warning:" || true

echo "== 4/6 生成 dex =="
"$BT/d8" --min-api 21 --lib "$AJAR" --output build/dex \
  $(find build/classes -name '*.class')

echo "== 5/6 打包与对齐 =="
cp build/base.apk build/withdex.apk
(cd build/dex && zip -q -j ../withdex.apk classes.dex)
"$BT/zipalign" -f -p 4 build/withdex.apk build/aligned.apk

echo "== 6/6 签名 =="
if [ ! -f "$KS" ]; then
  echo "  生成签名密钥：$KS"
  mkdir -p "$VAULT"
  chmod 700 "$VAULT" 2>/dev/null || true
  [ -f "$KP" ] || { head -c 24 /dev/urandom | base64 | tr -d '/+=' | cut -c1-20 > "$KP"; chmod 600 "$KP"; }
  "$JAVA_HOME/bin/keytool" -genkeypair -v -keystore "$KS" -alias daokedao \
    -keyalg RSA -keysize 2048 -validity 10950 \
    -storepass "$(cat "$KP")" -keypass "$(cat "$KP")" \
    -dname "CN=DaoKeDao Reader, O=DaoKeDao, C=CN" >/dev/null 2>&1
  chmod 600 "$KS"
fi
"$BT/apksigner" sign \
  --ks "$KS" --ks-pass "file:$KP" --key-pass "file:$KP" \
  --min-sdk-version 21 \
  --out "dist/道可道-易传-$VERNAME.apk" build/aligned.apk
"$BT/apksigner" verify --min-sdk-version 21 "dist/道可道-易传-$VERNAME.apk" | head -5

ls -la "dist/道可道-易传-$VERNAME.apk"
echo "✓ 完成：dist/道可道-易传-$VERNAME.apk"
