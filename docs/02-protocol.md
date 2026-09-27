# 02 — Auth protocol (all verified in `libstub.so` + Auth dex)

## Status request

- Native builds `action=login&key=<key>&device=<device>` and POSTs it to the
  status URL (XOR-`0x2A` blob @`0xd1a06`, 47 B → now our Worker `/auth`).
- AuthMain (Java, embedded dex) independently POSTs to its own copy of the URL
  (`https://app.lagx.online/sfloader/get_status.php`, 47 B → patched to Worker).
- Response handling (native, `nativeSubmitKey`):
  - len < 6 → fail. Contains `Error:` (memchr `'E'` + memcmp) → `onServerError`.
  - len != 7 → `Auth FAILED` → `onLoginFailed`.
  - `memcmp(resp, "Success", 7)` must equal 0 → download path.
- So the ONLY valid success body is exactly `Success` (7 bytes, no newline,
  no JSON). Any other shape fails. (GitHub Pages returns 405 to POST — that's
  why status lives on the Worker, not Pages.)

## Download request

- URL = XOR-`0x2A` blob @`0xd1a35` (49 B → now Pages `.../gv2/d.php`)
  + `?api_key=` + key halves + XOR blob @`0xd1a66` (`ActionMods_Secure_9921_Xentra`,
  untouched) + `&user_key=` + `&game=` + `&lib=`(`libsf<N>.so`) + `&device_id=`
  + `&version=`(`1.0.0`). Server ignores query — static file is fine.
- After download, a second fetch must return exactly `SUCCESS` (upper, 7 B)
  or `ERROR_OUTDATED` (14 B); anything else → fail. Plain HTTP 200 with the
  `.so` bytes satisfies this.
- File is `dlopen`ed (`RTLD_NOW`), `unlink`ed, `dlsym("JNI_OnLoad")` called
  with `(vm, NULL)`. Our ghost exports only `JNI_OnLoad` — sufficient.

## Verdict strings seen (Auth dex dispatcher, `contains()` checks)

`DeviceMismatch`, `DEVICE_LIMIT`, `Expired`/`EXPIRED`, `Invalid Key`,
`ACCESS DENIED`, `KEY EXPIRED`, `DEVICE MISMATCH`, `GAME_MISMATCH`,
`OUTDATED`/`UPDATE REQUIRED`, `VPN_DETECTED`, `SERVER ERROR`. Success =
absence of all of these + the native `Success` check above.

## Crypto details

- Native URL blobs: single-byte XOR `0x2A`, lengths 47/49/29. Same-size swaps only.
- Embedded Auth dex: hex string in `.rodata`; after ANY edit recompute adler32
  (`dex[8:12]`) + SHA-1 (`dex[12:32]`) or ART rejects it ("Could not find
  AuthMain class").
- Ghost menu strings: XOR + NEON (`veorq`) blobs; marquee HTML at file
  `0x99759` (139 B) decryptable with the keystream method in
  `scripts/blobB_decrypt.py`.
