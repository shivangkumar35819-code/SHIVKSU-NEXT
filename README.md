# SHIVKSU-NEXT root compatibility

The installed APK is identical to `Downloads/SHIVKSU-NEXT.apk`. Android accepts its APK signature, but the original bundled driver does not trust that certificate.

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

## Remaining verification

The custom driver has not yet been compiled or tested on the phone. After compilation, verify its build results, integrate it with the APK's patching flow, and prepare a boot-image patch from the phone's exact firmware. Identify and back up the correct partition before considering a separate flash action. A `.ko` file is not a boot image.

No boot partition, module installation, root policy, or bootloader setting was changed during these checks. One temporary diagnostic file was extracted, read, and removed from `/data/local/tmp`.
