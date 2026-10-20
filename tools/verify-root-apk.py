"""Check that every packaged driver trusts the actual APK signing certificate."""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zipfile

KMIS = ['android12-5.10', 'android13-5.10', 'android13-5.15', 'android14-5.15',
        'android14-6.1', 'android15-6.6', 'android16-6.12', 'android17-6.18']
MACHINES = {'arm64-v8a': 183, 'x86_64': 62}

def length_prefixed(data, offset=0):
    size = struct.unpack_from('<I', data, offset)[0]
    end = offset + 4 + size
    assert end <= len(data), 'Invalid signature field length'
    return data[offset + 4:end], end

def certificate(apk):
    eocd = apk.rfind(b'PK\x05\x06')
    assert eocd >= 0
    cd = struct.unpack_from('<I', apk, eocd + 16)[0]
    assert apk[cd - 16:cd] == b'APK Sig Block 42'
    block_size = struct.unpack_from('<Q', apk, cd - 24)[0]
    offset = cd - block_size
    while offset < cd - 24:
        pair_size = struct.unpack_from('<Q', apk, offset)[0]
        pair_id = struct.unpack_from('<I', apk, offset + 8)[0]
        end = offset + 8 + pair_size
        assert end <= cd - 24
        if pair_id == 0x7109871A:
            signers, _ = length_prefixed(apk[offset + 12:end])
            signer, _ = length_prefixed(signers)
            signed_data, _ = length_prefixed(signer)
            _, cert_offset = length_prefixed(signed_data)
            certificates, _ = length_prefixed(signed_data, cert_offset)
            cert, _ = length_prefixed(certificates)
            return cert
        offset = end
    raise AssertionError('APK v2 signature is missing')

apk_path = Path(sys.argv[1])
artifact_root = Path(sys.argv[2])
cert = certificate(apk_path.read_bytes())
cert_hash = hashlib.sha256(cert).hexdigest()
assert cert_hash == '996ec4da5ac204e00136f0dabf5605d613a9c5ac045514ee2eae266c89b3994a'
assert len(cert) == 0x4D8 and len(cert) <= 2048
expected = {f'assets/custom-lkm/{abi}/{kmi}_kernelsu.ko'
            for abi in MACHINES for kmi in KMIS}
with zipfile.ZipFile(apk_path) as archive:
    source_root = Path(__file__).resolve().parent.parent
    provenance = json.loads((source_root / 'custom-root/native-provenance.json').read_text())
    for abi, entry in provenance.items():
        native = archive.read(f'lib/{abi}/libksud.so')
        assert hashlib.sha256(native).hexdigest() == entry['sha256'], f'Unexpected daemon: {abi}'
    installer = archive.read('META-INF/com/google/android/update-binary')
    assert installer == (source_root / 'manager/scripts/update_binary.sh').read_bytes()
    assert b'assets/custom-lkm/$ARCH/${KMI}_kernelsu.ko' in installer
    packaged = {p for p in archive.namelist() if p.startswith('assets/custom-lkm/') and p.endswith('.ko')}
    assert packaged == expected, 'Missing or unexpected packaged drivers'
    for name in sorted(expected):
        abi, filename = name.split('/')[-2:]
        kmi = filename.removesuffix('_kernelsu.ko')
        data = archive.read(name)
        original = (artifact_root / abi / filename).read_bytes()
        assert data == original, f'Packaged driver differs from CI artifact: {name}'
        assert data[:6] == b'\x7fELF\x02\x01'
        assert struct.unpack_from('<H', data, 16)[0] == 1
        assert struct.unpack_from('<H', data, 18)[0] == MACHINES[abi]
        assert cert_hash.encode() in data, f'Driver does not trust APK certificate: {name}'
        assert b'com.rifsxd.ksunext' in data
        assert b'79e590113c4c4c0c222978e413a5faa801666957b1212a328e46c00c69821bf7' not in data
        versions = re.findall(rb'vermagic=([^\x00]+)', data)
        assert any(v.startswith(kmi.split('-')[1].encode() + b'.') for v in versions), name
        print(f'PASS {abi}/{filename}')
for checksum_file in artifact_root.glob('SHA256SUMS-*'):
    for line in checksum_file.read_text().splitlines():
        digest, relative = line.split(maxsplit=1)
        assert hashlib.sha256((artifact_root / relative).read_bytes()).hexdigest() == digest
print(f'PASS APK certificate: {len(cert)} bytes, SHA-256 {cert_hash}')
print(f'PASS all {len(expected)} packaged drivers and artifact checksums')
