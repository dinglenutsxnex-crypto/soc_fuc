# 06 — Branding cleanup (nexora/Discord, anti-ActionMods)

## App container (AMODVIP rebuild)

- `res/layout/activity_home.xml`: title `ACTIONMODS VM` → `fuck socum`;
  subtitle → `cracked by nexora` (14sp); new `tvDiscord` TextView with the
  invite URL + `android:onClick="openDiscord"` (autoLink was tried — text didn't
  render; plain text + handler works).
- `HomeActivity.smali` (dualappspro): added `openDiscord(View)` → VIEW intent.
- Settings drawer `layout_main_setting.xml`: telegram row `visibility=gone`;
  ADDED Discord row (`@+id/layout_discord`, reuses `ic_feedback` icon).
- `layout_setting_drawer.xml`: telegram entry gone. `activity_home` website
  subtitle blanked (later replaced by Discord line above).
- `strings.xml`: `app_name` → `SF4VIP`; telegram/plug strings neutralized.
- Launcher icons: all `mipmap-*/ic_launcher[_round].png` replaced with cropped
  field photo (PowerShell `System.Drawing`, center-crop square → 72/96/144/192).
- Views are hidden/blanked, never deleted (avoids NPEs in code holding refs).

## Ghost menu (`libsf4.so`, served via Pages `d.php`)

- Menu strings are XOR+NEON encrypted in native `.rodata`; dex strings contain
  NO branding (verified by sweep).
- Marquee HTML lives at file `0x99759` (139 B), keystream recovered by emulating
  the decrypt (`scripts/blobB_decrypt.py`, verified against known plaintext).
  Current text: `SF4 VIP | cracked by nexora | ...` (+ spaces pad to 139).
  Re-encrypt = XOR with same keystream (affine transform). Swap bytes in file.
- Menu title `SetText` call @`0x1250c` (`bl 0x127a4`) NOPed → blank title bar.
- Watchdog thread spawn @`0x13674/0x1367c` NOPed (8 B). Dex 100% stock otherwise
  (hand-edited dex variants FAIL ART verification — `VerifyError` in
  `com.android.support.Menu` — never ship those).
- Credit overlay (`DrawCredits` into DecorView) is killed via P7 in libstub,
  not in the ghost.
- Telegram button in menu: NOT in dex strings, NOT in marquee blob. Still
  unlocated (candidate: remaining encrypted blobs around `0xd7a98/0xd7ab0`,
  or the base64 icon PNG). Open item.

## Auth screens (payload dex in libstub)

- Outdated-version message (85 B, mentions action-mods.com) never triggers in
  our flow (server never sends OUTDATED). Left as-is deliberately.
- Promo/free-version dialogs + key UI text left functional (needed for key entry).
