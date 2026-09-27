"""Apply the 4 same-size patches to libstub.so (AMODSVM copy)."""
import struct

P = 'C:/Users/Aditya Yadav/Downloads/garbage/vip/AMODSVM_libstub_patched.so'
import zipfile
z = zipfile.ZipFile('C:/Users/Aditya Yadav/Downloads/garbage/vip/AMODSVM.apk')
d = bytearray(z.read('lib/arm64-v8a/libstub.so'))
print('libstub size:', len(d))

OLD_STATUS = b'https://app.lagx.online/sfloader/get_status.php'
NEW_STATUS = b'https://soc-fuc.adiforgottenme.workers.dev/auth'
OLD_DL = b'https://app.lagx.online/sfloader/download_mod.php'
NEW_DL = b'https://dinglenutsxnex-crypto.github.io/gv2/d.php'
assert len(OLD_STATUS) == len(NEW_STATUS) == 47, (len(OLD_STATUS), len(NEW_STATUS))
assert len(OLD_DL) == len(NEW_DL) == 49, (len(OLD_DL), len(NEW_DL))

# P1: native status blob @0xd1a06 is XOR-0x2A ciphertext -> write NEW^0x2A
o1 = 0xd1a06
assert bytes(d[o1:o1+47]) == bytes(c ^ 0x2A for c in OLD_STATUS), bytes(d[o1:o1+47])
d[o1:o1+47] = bytes(c ^ 0x2A for c in NEW_STATUS)
print('P1 status URL patched @', hex(o1))

# P2: native download blob @0xd1a35 (same scheme)
o2 = 0xd1a35
assert bytes(d[o2:o2+49]) == bytes(c ^ 0x2A for c in OLD_DL), bytes(d[o2:o2+49])
d[o2:o2+49] = bytes(c ^ 0x2A for c in NEW_DL)
print('P2 download URL patched @', hex(o2))

# P3: embedded binauth.dex URL (find lagx URL inside decoded dex region)
# locate hex blob start
hx = d.find(b'6465780a30333500')
print('hex blob @', hex(hx))
hexlen = 72600
hexblob = d[hx:hx+hexlen].decode()
dex = bytearray(bytes.fromhex(hexblob))
assert dex[:8] == b'dex\n035\x00'
i = dex.find(OLD_STATUS)
assert i != -1, 'lagx URL not in embedded dex!'
dex[i:i+47] = NEW_STATUS
print('P3 embedded dex URL patched @ dex+%s' % hex(i))
# P3b: fix dex header checksum (adler32) + signature (SHA-1)
import zlib, hashlib, struct
sig = hashlib.sha1(bytes(dex[32:])).digest()
dex[12:32] = sig
crc = zlib.adler32(bytes(dex[12:])) & 0xffffffff
struct.pack_into('<I', dex, 8, crc)
print('P3b dex header fixed: crc=%s sig=%s..' % (hex(crc), sig.hex()[:16]))
newhex = dex.hex().encode()
assert len(newhex) == hexlen
d[hx:hx+hexlen] = newhex
print('P3 hex swapped back, same length OK')

# P4: pin bypass @0x3a714: mov w0,#1; ret
o4 = 0x3a714
print('P4 site bytes:', bytes(d[o4:o4+8]).hex(' '))
d[o4:o4+8] = bytes.fromhex('20008052c0035fd6')
print('P4 pin check bypassed @', hex(o4))

# P5: expected APK cert hash @0xd1a83 (64B XOR-0x2A) -> OUR debug cert
o5 = 0xd1a83
OUR_HEX = '81CDE33956B378A1B06FC06B19DE6F147490DD3EA303D64A6084159B64884758'
cur = bytes(d[o5:o5+64])
dec = bytes(c ^ 0x2A for c in cur)
print('P5 current expected cert:', dec.decode())
assert len(dec) == 64 and all(chr(c) in '0123456789ABCDEF' for c in dec), 'unexpected P5 content!'
d[o5:o5+64] = bytes(c ^ 0x2A for c in OUR_HEX.encode())
print('P5 expected cert swapped to OUR debug cert @', hex(o5))

# P6: infinite game scan - NOP the B.HI timeout branch @0x3e810
o6 = 0x3e810
cur6 = bytes(d[o6:o6+4])
print('P6 site bytes:', cur6.hex(' '))
assert cur6[3] == 0x54 and (cur6[0] & 0x0F) == 0x08, 'not B.HI!'
d[o6:o6+4] = bytes.fromhex('1f2003d5')
print('P6 scan timeout removed @', hex(o6))

# P7: skip DrawCredits overlay - CBZ @0x3d790 -> B @0x3d934 (fail-forward to menu)
o7 = 0x3d790
cur7 = bytes(d[o7:o7+4])
print('P7 site bytes:', cur7.hex(' '))
assert cur7.hex(' ') == '20 0d 00 b4', 'not expected CBZ!'
d[o7:o7+4] = bytes.fromhex('69000014')
print('P7 DrawCredits skipped @', hex(o7))

open(P, 'wb').write(bytes(d))
print('WROTE', P, len(d))
