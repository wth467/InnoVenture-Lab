import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import binascii
from src.sm3_ref import hexdigest, sm3_hash, compress
from src.sm3_opt import sm3_single_block_fast

def _digest_to_state(digest: bytes):
    import struct
    return list(struct.unpack(">8I", digest))

def _sm3_padding_for_length(byte_len: int) -> bytes:
    ml = byte_len * 8
    pad = bytearray()
    pad.append(0x80)
    while ((byte_len + len(pad)) * 8) % 512 != 448:
        pad.append(0x00)
    pad += ml.to_bytes(8, "big")
    return bytes(pad)

def forge_mac(original_message: bytes, original_mac_hex: str, extra: bytes, guessed_key_len: int):
    orig_mac = binascii.unhexlify(original_mac_hex)
    state = _digest_to_state(orig_mac)
    total_len = guessed_key_len + len(original_message)
    padding = _sm3_padding_for_length(total_len)
    forged_message = original_message + padding + extra
    final_total_len = total_len + len(padding) + len(extra)
    cont = bytearray(extra)
    cont.append(0x80)
    while ((len(cont) + total_len + len(padding)) * 8) % 512 != 448:
        cont.append(0x00)
    cont += (final_total_len * 8).to_bytes(8, "big")
    V = state.copy()
    for i in range(0, len(cont), 64):
        blk = bytes(cont[i:i+64])
        V = compress(V, blk)
    forged_mac = b"".join(v.to_bytes(4, "big") for v in V)
    return forged_message, forged_mac.hex()

def test_length_extension_success():
    key = b"secret-key"
    message = b"comment=10"
    mac = hexdigest(key + message)
    guessed_key_len = len(key)  # 攻击者可以枚举多个长度进行尝试
    extra = b";admin=true"
    forged_msg, forged_mac = forge_mac(message, mac, extra, guessed_key_len)
    # 服务器端验证（有 key）
    server_mac = hexdigest(key + forged_msg)
    assert server_mac == forged_mac
