# Wild KSU custom build (separate from SHIVKSU-NEXT main)

This branch builds Wild KSU 3.1.1 for ARM64 / android15-6.6 with the public
identity in identity.json. Main remains the previous KernelSU-Next setup.

The signing key is only on the user's PC under .android/wild-ksu-release.
No private key or signing password is stored here or needed by GitHub Actions.

Binary build: Actions -> Build Wild KSU custom release binaries. The workflow
file keeps its previous build-shivksu-driver.yml filename so it can be manually
dispatched against this branch without modifying main.

The successful run is linked in local-build/BUILD-REPORT.md. It compiles the
module, tests/lints the loader, builds the static init and Android daemon, and
creates/verifies the patched gold OS3.0.4.0.VNQINXM boot image entirely on CI.
The firmware input is the provided stock boot image, compressed for storage.
It is not intended for other devices or firmware versions.

To reproduce the local Manager build from the original Wild KSU 3.1.1 source:

1. Apply local-build/manager-customization.patch to the source root.
2. Copy local-build/build-release.py, manager-cert.der, README.md and this
   directory's identity.json and verify-module.py into source/custom-root/.
3. Download wild-custom-release-binaries from the successful Actions run.
4. Restore the existing local signing directory if using a different PC.
5. Run build-release.py --binaries ARTIFACT_DIR --java-home JAVA_21_HOME.
   Android SDK 36, build tools 36.1.0 and NDK 29.0.14206865 are required.

For loader/daemon source reconstruction, copy loader/*.rs into
userspace/ksuinit/src and apply daemon-lint.patch. CI runs rustfmt before building.
The locally signed APK verifies the exact built assets, public signing identity,
APK signature schemes, package/ABI setup and recovery script packaging.

No workflow installs, reboots or flashes the phone. Device root testing remains
for the user. The standalone .ko file is not a flashable boot image.
