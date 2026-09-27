# 04 — Server side

## Cloudflare Worker (this repo)

`src/index.js`: `POST|GET /auth` → exactly `Success` (7 bytes, `text/plain`).
Everything else → `sfapi`. That's the whole API — the loader only needs the
verdict; all params are ignored.

Deploy: auto-deploys from `main` (`wrangler.toml`, `compatibility_date`).
After pushing, verify: `curl -X POST --data 'action=login&key=t&device=x'
https://soc-fuc.adiforgottenme.workers.dev/auth` must print `Success`.

## GitHub Pages (other repo `gv2`, `docs/`)

- `docs/d.php` = ghost `.so` BYTES (currently watchdog-neutered + nexora
  marquee build). Served with wrong content-type — irrelevant, loader writes
  raw bytes to disk. Any size OK.
- `docs/api`, `docs/sapi`, `docs/s` = legacy attempts (Pages returns 405 to
  POST — unusable for status, left for reference). Do NOT point the status URL
  at Pages.
- After pushing a new `d.php`, wait ~60 s (Pages rebuild), then
  hash-verify the download matches before telling the user to re-auth
  (loader `unlink`s after load, so re-auth re-downloads).

## Local fallback (`scripts/sfapi_local.py`)

Stdlib POST/GET server answering `Success` for `127.0.0.1:8000`. Kept as
backup (Termux on device). Not currently used since Worker works.
