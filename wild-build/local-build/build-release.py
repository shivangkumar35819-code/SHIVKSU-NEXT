"""Build with the persistent local key; never put signing secrets in GitHub."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile
import zlib

parser = argparse.ArgumentParser()
parser.add_argument("--binaries", type=Path, required=True)
parser.add_argument("--java-home", type=Path, required=True)
parser.add_argument("--worktree", type=Path, default=Path.home() / ".android/wild-ksu-build-20261020")
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
identity = json.loads((root / "custom-root/identity.json").read_text())
binaries = args.binaries.resolve()
for line in (binaries / "SHA256SUMS").read_text().splitlines():
    expected, filename = line.split(maxsplit=1)
    assert hashlib.sha256((binaries / filename.strip()).read_bytes()).hexdigest() == expected
assert json.loads((binaries / "identity.json").read_text()) == identity
subprocess.run(["python", str(root / "custom-root/verify-matrix.py"),
                str(root / "custom-root/identity.json"), str(binaries)], check=True)

# Verify RustEmbed really contains these exact built files, not upstream assets.
daemon = (binaries / "libksud.so").read_bytes()
assert daemon[:4] == b"\x7fELF" and struct.unpack_from("<H", daemon, 18)[0] == 183
expected_assets = {name: (binaries / name).read_bytes()
                   for name in ["ksuinit", *[kmi + "_kernelsu.ko" for kmi in identity["supported_kmis"]]]}
init = expected_assets["ksuinit"]
assert init[:4] == b"\x7fELF" and struct.unpack_from("<HH", init, 16) == (2, 183)
program_offset = struct.unpack_from("<Q", init, 32)[0]
entry_size, entry_count = struct.unpack_from("<HH", init, 54)
assert all(struct.unpack_from("<I", init, program_offset + index * entry_size)[0] != 3
           for index in range(entry_count)), "Early init must be static (no PT_INTERP)"
found = set()
for offset, first in enumerate(daemon):
    # include-flate 0.3.1 stores raw DEFLATE without a gzip/zlib header.
    if first & 6 not in (2, 4):
        continue
    try:
        prefix = zlib.decompressobj(-15).decompress(daemon[offset:offset + 1024], 4)
        if prefix != b"\x7fELF":
            continue
        stream = zlib.decompressobj(-15)
        data = stream.decompress(memoryview(daemon)[offset:], 16 * 1024 * 1024)
    except zlib.error:
        continue
    if stream.eof:
        found.update(name for name, expected in expected_assets.items() if data == expected)
assert found == set(expected_assets), f"Missing embedded custom assets: {set(expected_assets) - found}"
assert b"init_module failed after replacing vermagic" in expected_assets["ksuinit"]
print("Verified exact custom module and rebuilt loader inside daemon")

settings = json.loads((Path.home() / ".android/wild-ksu-release/signing.json").read_text())
env = os.environ.copy()
env.update({
    "JAVA_HOME": str(args.java_home.resolve()),
    "ANDROID_HOME": str(Path.home() / ".android/sdk"),
    "ORG_GRADLE_PROJECT_KEYSTORE_FILE": settings["keystore"],
    "ORG_GRADLE_PROJECT_KEYSTORE_PASSWORD": settings["password"],
    "ORG_GRADLE_PROJECT_KEY_ALIAS": settings["alias"],
    "ORG_GRADLE_PROJECT_KEY_PASSWORD": settings["password"],
    "DEBUG": "",
})
env["PATH"] = str(args.java_home.resolve() / "bin") + os.pathsep + env["PATH"]
shutil.copy2(binaries / "libksud.so", root / "manager/app/src/main/jniLibs/arm64-v8a/libksud.so")
worktree = args.worktree.resolve()
for directory in ["manager", "scripts"]:
    shutil.copytree(root / directory, worktree / directory, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("build", ".gradle", ".kotlin", ".cxx",
                                                 "local.properties", "*.jks", "*.keystore"))
with (root / ".build-tools/custom-release.log").open("w") as log:
    subprocess.run(["cmd.exe", "/c", "gradlew.bat", "assembleRelease", "-PwildCustomArm64=true", "-PwildAllKernels=true",
                    "--console=plain"], cwd=worktree / "manager", env=env,
                   stdout=log, stderr=subprocess.STDOUT, check=True)
apk = worktree / "manager/app/build/outputs/apk/release/Wild_KSU_v3.1.1-custom-all_33208-release.apk"
signer = Path(env["ANDROID_HOME"]) / "build-tools/36.1.0/apksigner.bat"
result = subprocess.run(["cmd.exe", "/c", str(signer), "verify", "--verbose", "--print-certs", str(apk)],
                        env=env, capture_output=True, text=True, check=True)
assert identity["certificate_sha256"] in result.stdout
assert "CN=Android Debug" not in result.stdout
assert "Verified using v2 scheme (APK Signature Scheme v2): true" in result.stdout
assert "Verified using v1 scheme (JAR signing): false" in result.stdout
assert "Verified using v3 scheme (APK Signature Scheme v3): false" in result.stdout
with zipfile.ZipFile(apk) as archive:
    assert archive.read("lib/arm64-v8a/libksud.so") == daemon
    assert all(not name.startswith("lib/") or name.startswith("lib/arm64-v8a/") for name in archive.namelist())
    assert archive.read("META-INF/com/google/android/update-binary")
    assert archive.read("META-INF/com/google/android/updater-script")
dist = root / "dist/Wild-KSU-custom-all-supported-arm64"
dist.mkdir(parents=True, exist_ok=True)
for item in binaries.iterdir():
    if item.is_file():
        shutil.copy2(item, dist / item.name)
shutil.copy2(apk, dist / apk.name)
shutil.copy2(root / "custom-root/manager-cert.der", dist / "manager-cert.der")
shutil.copy2(root / "custom-root/README.md", dist / "README.txt")
(dist / "APK-SIGNATURE.txt").write_text(result.stdout)
checksums = [f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.name}"
             for item in sorted(dist.iterdir()) if item.is_file() and item.name != "SHA256SUMS"]
(dist / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
print("Signed release verified:", dist / apk.name)
print("Bundle:", dist)
