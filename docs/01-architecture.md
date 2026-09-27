# 01 — Architecture

## Pieces

| Piece | What | Where |
|---|---|---|
| Container base | `AMODSVM.apk` (~80 MB, pkg `com.actionmods.vm`, v1.1) | local `vip/` |
| Shipped build | `AMODVIP.apk` (modded base, v1.1-sf4vip) | local `vip/`, installed on phone |
| Loader native | `lib/arm64-v8a/libstub.so` (1,050,952 B, SONAME `libstub.so`) | inside APK, patched (see 03) |
| 2nd-stage native | `actionmods/lib/arm64.so` (944,160 B, needs `libfancy-bypass.so`) | inside APK, loaded from APK directly — **must stay STORED + 4096-aligned** |
| Origin container | `actionmods/origin.apk` (44 MB, clean sherrytse 1.2.4.10) | inside APK, untouched |
| Auth payload dex | embedded in libstub as 72,600-char hex @file `0xbf876` (36,300 B dex, 45 classes, `com.actionmods.AuthMain`) | patched URL + fixed header (see 03) |
| Ghost (menu) | `libsf4.so` (768,344 B, 1 export `JNI_OnLoad` @`0x135b0`, menu dex `com.android.support.Menu` inside) | served from Pages, NOT in APK |
| Auth server | Cloudflare Worker in this repo (`/auth`) | live |
| Ghost CDN | GitHub Pages, other repo (`gv2`, `docs/d.php`) | live |

## Load chain (verified with IDA + logcat)

1. `ActionmodsApp.<clinit>` → `System.loadLibrary("stub")` → `JNI_OnLoad`
   (`0x3e988`): saves `vm` @`0x1100D0`, spawns thread `sub_3E6E0`, detaches.
2. Thread: main proc aborts ("waiting for proxy"); colon-suffixed procs
   (`:hub`) scan for game activities every 2 s, forever (P6 removed 15-attempt cap):
   - `com.nekki.shadowfight` + `FCMNekkiUnityPlayerActivity` → id 2
   - `com.nekki.shadowfight3` + `NekkiNativeActivity` → id 3
   - `com.nekki.shadowfightarena` + `NekkiNativeActivity` → id 4
3. On detect: `sub_3DE60` (binAuth) decodes embedded hex → dex → loads
   `AuthMain` → key dialog → `submitKey` → `nativeSubmitKey` (`0x3cc44`).
4. `nativeSubmitKey`: cert check `sub_3C344` (P5 passes) → POST
   `action=login&key=&device=` to status URL (P1) → response must be exactly
   `Success` (len 7 + memcmp, see 02) → build download URL from blobs (P2) +
   params → download ghost → `dlopen` → `unlink` (hide) → `dlsym("JNI_OnLoad")`
   → call `(vm, NULL)` → menu thread starts. Then `DrawCredits` is SKIPPED (P7)
   and flow continues to menu.

## Processes (logcat tags: `ActionMods`)

- `com.actionmods.vm` — hub UI, stands down.
- `com.actionmods.vm:hub` — proxy/scanner/injector. Key dialog + auth run here.
- Clone game proc — ghost + menu live here.
