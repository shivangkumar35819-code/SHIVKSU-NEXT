"""Check the module's public manager identity before embedding it."""
import hashlib
import json
from pathlib import Path
import struct
import re
import sys

identity = json.loads(Path(sys.argv[1]).read_text())
data = Path(sys.argv[2]).read_bytes()
assert data[:4] == b"\x7fELF"
assert struct.unpack_from("<HH", data, 16) == (1, 183), "Expected ARM64 ET_REL"
assert identity["certificate_sha256"].encode() in data
assert identity["package"].encode() in data
assert 0 < identity["certificate_size"] <= 1024
family = Path(sys.argv[2]).name.removesuffix("_kernelsu.ko")
assert family in identity.get("supported_kmis", [identity["kmi"]])
kernel_version = family.split("-")[1].encode() + b"."
assert any(version.startswith(kernel_version)
           for version in re.findall(rb"vermagic=([^\x00]+)", data)), "Wrong kernel family"
print("Verified module manager identity:", identity)
print("Module SHA256:", hashlib.sha256(data).hexdigest())
