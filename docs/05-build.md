# 05 — APK build pipeline (Windows PC, no root needed on phone)

Tools (local `_tools/`): JDK 17, apktool 2.11.1, `btools-tmp/android-14`
(zipalign/apksigner/aapt2), MinGit (`git/cmd/git.exe`), SDK platform-tools
(adb), debug.keystore (`android`/`android`).

## Decode (once)

```
java -jar apktool.jar d AMODSVM.apk -o work/amod-base -f
```

## Per build

1. Copy patched `libstub.so` → `work/amod-base/lib/arm64-v8a/libstub.so`.
2. Res/smali edits as needed.
3. `apktool.jar b work/amod-base -o work/amodvip-unsigned.apk`
4. **`zipalign -p -f 4 unsigned aligned`** — `-p` is MANDATORY (page-aligns
   `actionmods/lib/arm64.so`, which is `dlopen`ed straight from the APK;
   without it: `UnsatisfiedLinkError ... not found` → instant close).
5. `apksigner sign --ks debug.keystore ...` (debug cert hash must match P5!).
6. `adb install -r AMODVIP.apk`.

Version: bump `apktool.yml` (`versionCode`, `versionName`, e.g. `1.1-sf4vip`).

## Gotchas hit before

- `res/layout/item_home.xml` had a duplicate `layout_height` (aapt2 strictness) —
  fixed once in the decode tree.
- `pageSizeCompat` (API 36 attr) breaks apktool's aapt on the stock GMS base —
  removed there (not present in AMODSVM base).
- apktool compresses `lib/` `.so` files (harmless, they're extracted at install
  since `extractNativeLibs=true`), but `actionmods/*` MUST stay STORED.
- Same package `com.actionmods.vm` + new cert = must uninstall-then-install if
  the original was ever installed (signature mismatch blocks update).

## On-device debugging (phone stays on USB)

- `adb logcat -d -v time -s 'ActionMods:D'` — loader narrates everything
  (scan attempts, `Target game N detected`, binAuth, `Auth FAILED`, pin,
  `Ghost Mod Injected!`).
- `adb shell monkey -p com.actionmods.vm -c android.intent.category.LAUNCHER 1`
  launches it remotely. Tombstones: `logcat -d | grep -A30 'Build fingerprint'`.
- `adb shell appops get com.actionmods.vm SYSTEM_ALERT_WINDOW` — menu overlay
  permission (must be `allow`, else menu can't draw).
