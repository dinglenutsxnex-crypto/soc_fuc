# 07 — Status + known issues (2026-09-27)

## Working (verified on device via adb/logcat)

- App opens, no instaclose. Scanner finds SFA clone (`Target game 4 detected`).
- Auth dex loads, key dialog shows, ANY key → Worker `Success` → ghost downloads
  → `Ghost Mod Injected!` → menu with all 26 features in-game.
- Overlay permission granted → menu draws. Credit overlay removed.
- Branding: app header/link/drawer/icon + menu marquee done (see 06).

## Known issues

1. **Post-win crash (match → main menu).** Tombstone: Unity main thread SIGTRAP
   inside `libunity`/`libil2cpp` after ~5 min — the GAME's own integrity check
   tripping on modded stats (server-reconciled online game). Phone is stock,
   unrooted — not environmental. Mitigation in progress: isolate by feature
   (all-OFF baseline, then one-by-one; suspects: Autowin/Instant Win/One Hit
   Kill/Max Upgrade). Loader-side cannot fix game-side integrity.
2. **Occasional freezes** — likely clone weight on device, under investigation.
3. **Ghost VerifyError risk**: only EVER serve dex-untouched ghost builds.
   Stock dex + 8-byte watchdog NOP = current live build.
4. **VPN/sniffer**: user has Octohide VPN + PCAPdroid installed. Either ACTIVE
   during auth = request aborted by loader + possible flag. Must stay off.
5. **Overlay perm**: re-check after reinstalls (`appops get`).
6. **Telegram button in menu**: unlocated (see 06). Marquee carries the invite
   as visible text; app drawer row is the clickable one.

## Test checklist for any new build

1. `adb install -r`, launch, `logcat -s ActionMods:D`: scanner attempts → ∞.
2. Launch SFA clone → `Target game 4` → binAuth loads (no `Could not find AuthMain`).
3. Enter key → Worker sees hit (or check logcat `Auth SUCCESS` + `Ghost Mod Injected!`).
4. Menu icon in game; overlay granted; no credit overlay.
5. Win a match with cheats OFF → menu transition clean? Then per-feature.
