"""Emulate blob-B decrypt (0x12528-0x12618) to read the menu HTML."""
import re

d = open('C:/Users/Aditya Yadav/Downloads/garbage/vip/libsf4.so', 'rb').read()
lines = open('C:/Users/ADITYA~1/AppData/Local/Temp/initdump.txt').read().splitlines()

# registers: w-regs (low 32 of x), q-regs 16 bytes. mem base x8 = blob (bss). emulate on ZERO blob to get keystream.
mem = bytearray(0x100)  # blob space
key = d[0x6fd20:0x6fd20+16]
W = {}
Q = {}
started = False
ops = 0
for l in lines:
    m = re.match(r'(0x[0-9a-f]+): (\w+) (.*)', l)
    if not m:
        continue
    a, mn, op = m.groups()
    a = int(a, 16)
    if a < 0x12528 or a > 0x12618:
        continue
    if mn == 'ldrb':
        # ldrb wD, [x8, #off]
        mm = re.match(r'w(\d+), \[x8, #(.+)\]', op)
        if mm:
            W[int(mm.group(1))] = mem[int(mm.group(2), 0)]
    elif mn == 'ldp':
        # ldp qA, qB, [x8] or [x8, #off]
        mm = re.match(r'q(\d+), q(\d+), \[x8(?:, #(.+))?\]', op)
        if mm:
            off = int(mm.group(3), 0) if mm.group(3) else 0
            Q[int(mm.group(1))] = bytearray(mem[off:off+16])
            Q[int(mm.group(2))] = bytearray(mem[off+16:off+32])
    elif mn == 'ldr' and op.startswith('q4'):
        Q[4] = bytearray(key)
    elif mn == 'mov':
        mm = re.match(r'w(\d+), #(.+)', op)
        if mm:
            W[int(mm.group(1))] = int(mm.group(2), 0) & 0xFF
    elif mn == 'movk':
        pass  # w8/w9 immediates not used in eors here (checked: w15/w0/w17/w10/w12/w9/w11/w13/w17 used; movk targets w8/w9)
    elif mn == 'eor' and '.16b' in op:
        # eor vD.16b, vA.16b, vB.16b
        mm = re.match(r'v(\d+).16b, v(\d+).16b, v(\d+).16b', op)
        if mm:
            dd, aa, bb = int(mm.group(1)), int(mm.group(2)), int(mm.group(3))
            Q[dd] = bytearray(x ^ y for x, y in zip(Q[aa], Q[bb]))
    elif mn == 'eor' and '.16b' not in op:
        # eor wD, wA, wB-or-imm
        mm = re.match(r'w(\d+), w(\d+), (w(\d+)|#(.+))', op)
        if mm:
            dd, aa = int(mm.group(1)), int(mm.group(2))
            if mm.group(4) is not None:
                W[dd] = (W[aa] ^ W[int(mm.group(4))]) & 0xFF
            else:
                W[dd] = (W[aa] ^ int(mm.group(5), 0)) & 0xFF
    elif mn == 'strb':
        mm = re.match(r'w(\d+), \[x8, #(.+)\]', op)
        if mm:
            mem[int(mm.group(2), 0)] = W[int(mm.group(1))]
    elif mn == 'stp':
        mm = re.match(r'q(\d+), q(\d+), \[x8(?:, #(.+))?\]', op)
        if mm:
            off = int(mm.group(3), 0) if mm.group(3) else 0
            mem[off:off+16] = Q[int(mm.group(1))]
            mem[off+16:off+32] = Q[int(mm.group(2))]
    elif mn == 'str':
        mm = re.match(r'q(\d+), \[x8\]', op)
        if mm:
            mem[0:16] = Q[int(mm.group(1))]
    ops += 1
print('ops emulated:', ops)
ks = bytes(mem[:139])
open('C:/Users/ADITYA~1/AppData/Local/Temp/blobB_ks.bin', 'wb').write(ks)
print('keystream saved')
# decrypt actual
ct = d[0x99759:0x99759+139]
pt = bytes(c ^ k for c, k in zip(ct, ks))
print('PLAINTEXT:')
print(pt.decode('utf-8', 'replace'))
open('C:/Users/ADITYA~1/AppData/Local/Temp/blobB_pt.bin', 'wb').write(pt)
