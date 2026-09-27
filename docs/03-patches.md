# 03 — Binary patches (`scripts/applypatch.py` is truth)

Target: `lib/arm64-v8a/libstub.so` from `AMODSVM.apk` (1,050,952 B).
IDA file addrs == file offsets for `.text`/`.rodata` here (imagebase 0).
ALL patches are same-size. Re-run script from the ORIGINAL each time.

| # | Addr | Orig | Patched | Why |
|---|---|---|---|---|
| P1 | `0xd1a06` (47 B) | `https://app.lagx.online/sfloader/get_status.php` ^`0x2A` | Worker `/auth` URL ^`0x2A` | status repoint |
| P2 | `0xd1a35` (49 B) | `https://app.lagx.online/sfloader/download_mod.php` ^`0x2A` | Pages `.../gv2/d.php` ^`0x2A` | download repoint |
| P3 | hex blob @`0xbf876` (72,600 ch) | embedded dex with lagx URL @dex+`0x7652` | same URL→Worker (47→47) + adler32/SHA-1 recomputed | AuthMain's own POST repoint |
| P4 | `0x3a714` (8 B) | func prologue | `mov w0,#1; ret` (`20008052c0035fd6`) | SSL pinning always-pass (`sub_3A714` compares server SPKI vs pinned) |
| P5 | `0xd1a83` (64 B) | their cert SHA-256 hex ^`0x2A` (`4B5DA7F0…`) | our debug cert SHA-256 hex ^`0x2A` (`81CDE339…`) | APK self-sig check passes legitimately |
| P6 | `0x3e810` (4 B) | `B.HI` timeout (`48070054`) | NOP (`1f2003d5`) | game scan runs forever (was 15×2 s) |
| P7 | `0x3d790` (4 B) | `CBZ X0` (`200d00b4`) | `B` to same target (`69000014`) | skip DrawCredits credit overlay, fail-forward into menu flow |

Current live URLs (both length-locked, do NOT change length without redoing):

- Status (47): `https://soc-fuc.adiforgottenme.workers.dev/auth`
- Download (49): `https://dinglenutsxnex-crypto.github.io/gv2/d.php`

## Anti-tamper map (libstub)

- `sub_3C344`: maps X-RAY (`com.actionmods.vm` + `.apk`), `unzip -p APK META-INF/*.RSA`,
  X.509→SHA-256→hex vs P5 blob, `exit()` on fail. Called from `nativeSubmitKey` only.
- `sub_3A714`: SPKI pin check (P4 bypasses). Callers `0x3b4c0/0x3bc88`.
- VPN/sniffer/MITM detectors kill the request — keep VPN and PCAPdroid OFF on device.
- Ghost `libsf4.so` has its own watchdog (`0x13674/0x1367c` pthread spawn → `_exit`);
  served ghost has those 2 insns NOPed (8 B total, dex untouched).
- `NPProtect`/`npkill` = protector annotations, not killers. No Java startup killer found.
