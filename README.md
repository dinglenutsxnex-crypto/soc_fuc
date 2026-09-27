# SF4VIP — keyless Shadow Fight 4 mod loader

Self-hosted clone of the ActionMods SF4 pipeline. Any key works. No ActionMods
servers involved anywhere.

## How it works (30 seconds)

1. `AMODVIP.apk` (modded `AMODSVM.apk` base) runs SFA inside its container.
2. On key submit, patched `libstub.so` POSTs to **our** Cloudflare Worker
   (`/auth` in this repo, `src/index.js`) instead of `app.lagx.online`.
3. Worker answers exactly `Success` (7 bytes). Loader downloads the ghost
   (`libsf4.so` menu) from GitHub Pages (`gv2` repo, `docs/d.php`) and injects it.
4. Menu appears in-game. Branding stripped, nexora/Discord branding applied.

## Repo layout

- `src/index.js` + `wrangler.toml` — the live Worker. DO NOT BREAK: the mod
  phones home here on every key submit.
- `docs/*.md` — full knowledge dump (protocol, patches, build, status).
- `scripts/` — patch applier + helpers (paths are for the original PC).

## Live endpoints (must keep serving)

- `POST https://soc-fuc.adiforgottenme.workers.dev/auth` → `Success` (7 bytes)
- `GET https://dinglenutsxnex-crypto.github.io/gv2/d.php` → ghost `.so` bytes

## For the next AI

Read in order: `docs/01-architecture.md`, `docs/02-protocol.md`,
`docs/03-patches.md`, `docs/04-server.md`, `docs/05-build.md`,
`docs/06-branding.md`, `docs/07-status.md`. Then `scripts/applypatch.py`
is the executable source of truth for every binary patch.
