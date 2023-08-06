#!/usr/bin/env python
# -*- coding: utf-8 -*-
import binascii
with open("/opt/linotp/etc/linotp2/encKey", 'rb') as f:
    secret = f.read(32)

iv_hex = "6f6b636270f7d2c99ae79c8389cc708c"
data_hex = "bb2263409697c6c330086d755866122ce788f10f4d7598af17dcbf7f9b9e595a1b6c980da5a4b10553320c5759cc773742b0e124e9c4c3b76fd6f20a6e1c26e23fd5152aba7a7b82f3b363053ca363831e39a61220bd6280ce7c956138fcb2b1"

iv = binascii.unhexlify(iv_hex)
#data = binascii.unhexlify(data_hex)
data = data_hex
from Crypto.Cipher import AES

aesObj = AES.new(secret, AES.MODE_CBC, iv)
output = aesObj.decrypt(data)

eof = len(output) - 1
if eof == -1:
    raise Exception('invalid encoded secret!')

while output[eof] == '\0':
    eof -= 1
#if output[eof - 1:eof + 1] != '\x01\x02':
#    raise Exception('invalid encoded secret!')
# convert output from ascii, back to bin data
b = len(output)
data = binascii.a2b_hex(output)
print(data)