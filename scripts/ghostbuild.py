"""Ghost rebrand build: blobB swap + title-call NOP on watchdog-neutered base."""
import shutil

shutil.copy('C:/Users/ADITYA~1/AppData/Local/Temp/ghost_nowd.so',
            'C:/Users/ADITYA~1/AppData/Local/Temp/ghost_brand.so')
p = 'C:/Users/ADITYA~1/AppData/Local/Temp/ghost_brand.so'
d = bytearray(open(p, 'rb').read())

# 1. blob B ciphertext swap @file 0x99759 (139B)
newct = open('C:/Users/ADITYA~1/AppData/Local/Temp/blobB_new.bin', 'rb').read()
assert len(newct) == 139
d[0x99759:0x99759+139] = newct
print('blobB swapped')

# 2. title setText call NOP @0x1250c (bl 0x127a4 -> nop)
cur = bytes(d[0x1250c:0x1250c+4])
print('title call bytes:', cur.hex(' '))
assert cur.hex(' ') == 'a6 00 00 94', 'unexpected!'
d[0x1250c:0x1250c+4] = bytes.fromhex('1f2003d5')
print('title call NOPed')

open(p, 'wb').write(bytes(d))
print('WROTE ghost_brand.so')

# verify marquee decrypts to new text
ks = open('C:/Users/ADITYA~1/AppData/Local/Temp/blobB_ks.bin', 'rb').read()
pt = bytes(c ^ k for c, k in zip(bytes(d[0x99759:0x99759+139]), ks))
print('verify:', pt.decode())
