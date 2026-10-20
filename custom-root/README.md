# Custom driver build

See the repository README for current compatibility and build instructions.

These 16 driver files were reused from the existing local custom build and
individually checked for the manager signing identity, ABI, KMI and checksums.
They were not freshly compiled during this APK release. Rebuild from the
pinned upstream source using `.github/workflows/build-shivksu-driver.yml`.
The workflow applies `certificate-support.patch` and retains exact certificate
size and SHA-256 authentication. No private key is required to compile drivers.

The old `manager-customization.patch` is a historical reference. The current
manager source is tracked directly under `manager/`.
