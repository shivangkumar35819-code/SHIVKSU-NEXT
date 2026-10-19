"""Reject missing, extra, mismatched or unsigned-identity driver artifacts."""
import json
from pathlib import Path
import subprocess
import sys

identity = json.loads(Path(sys.argv[1]).read_text())
directory = Path(sys.argv[2])
expected = {kmi + "_kernelsu.ko" for kmi in identity["supported_kmis"]}
actual = {path.name for path in directory.glob("*.ko")}
assert actual == expected, f"Missing {expected - actual}; unexpected {actual - expected}"
for name in sorted(expected):
    subprocess.run([sys.executable, str(Path(__file__).with_name("verify-module.py")),
                    sys.argv[1], str(directory / name)], check=True)
print(f"Verified complete matrix: {len(expected)} matching ARM64 kernel modules")
