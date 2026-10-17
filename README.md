# SHIVKSU-NEXT root compatibility

During diagnosis, the installed APK matched the initial `Downloads/SHIVKSU-NEXT.apk` build. Android accepted its APK signature, but the original bundled driver did not trust that certificate. The replacement APK now packages the matching custom drivers described below; it has not been installed or boot-tested on the phone during this build.

Confirmed from the installed APK and its extracted ARM64 android15-6.6 driver:

| Setting | Installed custom APK | Original driver |
| --- | --- | --- |
| Certificate size | 1240 bytes (`0x4d8`) | Expects 998 bytes (`0x3e6`); maximum 1024 |
| Certificate SHA-256 | `996ec4da5ac204e00136f0dabf5605d613a9c5ac045514ee2eae266c89b3994a` | `79e590113c4c4c0c222978e413a5faa801666957b1212a328e46c00c69821bf7` |
| Package | `com.rifsxd.ksunext` | A matching certificate is still required |

The connected phone reports Android 15, ARM64, kernel `6.6.118-android15-8-ge56cf6b09cca-ab15511674-4k`, and an already loaded KernelSU LKM with version 33355 / UAPI 5. A loaded driver does not establish that this manager can receive root permission.

## Prepared fix

`certificate-support.patch` keeps exact certificate-size and SHA-256 checks. It raises the bounded certificate limit to 2048 bytes and reads the certificate into a temporary heap allocation, freeing it on each exit path. It does not increase the kernel stack buffer or disable manager verification.

The manual workflow `.github/workflows/build-shivksu-driver.yml` builds ARM64 and x86-64 LKMs from upstream commit `4c706b5938665866ebe16944a481a7b91e3396af` with this patch, this APK's public certificate size/hash, and its exact package. The signing keystore remains on the local PC; the workflow does not need it.

Supported build matrix: `android12-5.10`, `android13-5.10`, `android13-5.15`, `android14-5.15`, `android14-6.1`, `android15-6.6`, `android16-6.12`, and `android17-6.18`. Each KMI is compiled for both architectures, giving 16 driver files. This matrix does not establish compatibility with every OEM kernel or add support for 32-bit and non-GKI phones.

The workflow, patch, and `custom-root/build-x86_64.sh` must be present together in the GitHub repository. Run **Build SHIVKSU-NEXT drivers** under Actions to produce `SHIVKSU-NEXT-all-supported-drivers`. Running the workflow is a build step, not a phone installation.

`custom-root/manager-customization.patch` records the manager source changes against the original 3.4.2 archive, including branding, automatic custom-driver selection, unsupported-kernel checks, and installer error reporting. Copy the two ABI directories from the successful driver artifact into `manager/app/src/main/assets/custom-lkm/` before building the APK with the existing local signing key. See `ROOT-SETUP.txt` for the initial-install requirements.

## Remaining verification

All 16 custom drivers compiled and passed the GitHub Actions checks in run `39053044477`. The signed release APK was built locally. Its signature, certificate size/hash, all 16 packaged driver identities, artifact checksums, and packaged recovery script were verified. The recovery script also passed a non-executing Android shell syntax check.

Device boot/root testing remains undone. Use a boot-image source from the particular phone's exact firmware, identify and back up the correct partition, and review a separate flash action before device testing. A `.ko` file is not a boot image. The final APK alone does not replace the original driver already loaded on the phone.

No boot partition, module installation, root policy, or bootloader setting was changed during these checks. One temporary diagnostic file was extracted, read, and removed from `/data/local/tmp`.
