# SHIVKSU NEXT

Android root manager based on KernelSU-Next v3.4.2, upstream commit
`4c706b5938665866ebe16944a481a7b91e3396af`. App label and home title: **SHIVKSU NEXT**.
Version: `v3.4.2-shiv.1` (33356). Package remains `com.rifsxd.ksunext` because the
custom kernel drivers authenticate that package and the existing local signing certificate.

## LKM compatibility

Includes 16 custom drivers: ARM64 and x86_64 for each of these GKI KMIs:

`android12-5.10`, `android13-5.10`, `android13-5.15`, `android14-5.15`,
`android14-6.1`, `android15-6.6`, `android16-6.12`, `android17-6.18`.

The manager selects the matching custom driver during boot-image patching.
Recovery installation uses the same custom drivers. Unsupported KMIs stop with
an error instead of selecting an upstream driver with a different signing identity.
This does **not** support every phone, every OEM kernel, 32-bit Android, or every
root implementation. Installing the APK alone does not install a kernel driver.
Device boot/root operation has not been tested for this release.

## Build

Install JDK 21 and Android SDK platform 36, build-tools 36.1.0, and NDK
29.0.14206865. Set `JAVA_HOME` and `ANDROID_HOME`.

The native daemons in `manager/app/src/main/jniLibs` are unmodified official
v3.4.2 release binaries. The custom `.ko` files were compiled from the pinned
upstream commit with `custom-root/certificate-support.patch`; their public
signing identity is checked by `tools/verify-root-apk.py`. Rebuild them with
the **Build SHIVKSU-NEXT drivers** Actions workflow.

Set these environment variables using your local keystore (never commit it):

```
ORG_GRADLE_PROJECT_KEYSTORE_FILE
ORG_GRADLE_PROJECT_KEYSTORE_PASSWORD
ORG_GRADLE_PROJECT_KEY_ALIAS
ORG_GRADLE_PROJECT_KEY_PASSWORD
```

Then run:

```
cd manager
./gradlew assembleRelease
```

On Windows use `gradlew.bat`. Verify the result:

```
python tools/verify-root-apk.py manager/app/build/outputs/apk/release/SHIVKSU_NEXT_v3.4.2-shiv.1_33356-release.apk manager/app/src/main/assets/custom-lkm
```

The certificate SHA-256 must be
`996ec4da5ac204e00136f0dabf5605d613a9c5ac045514ee2eae266c89b3994a`.
Changing the APK signing certificate also requires rebuilding the custom drivers.

## Install

Use the phone's exact firmware boot image and the matching KMI. Keep its stock
image for recovery. Consult the upstream project documentation linked in `docs/README.md`.
The separate `.ko` files are kernel modules, not partition images.

Upstream source and notices are retained under GPL-3.0; see `LICENSE` and `docs/README.md`.
