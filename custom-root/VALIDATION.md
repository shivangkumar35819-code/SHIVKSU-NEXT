# Release validation: v3.4.2-shiv.1

- Gradle assembleRelease: passed (JDK 21, Android SDK 36, NDK 29).
- APK versionCode: 33356; package: com.rifsxd.ksunext.
- aapt application label: SHIVKSU NEXT; home toolbar reads the same app_name resource.
- apksigner verify: passed, APK Signature Scheme v2.
- Signing certificate: 1240 bytes; SHA-256 996ec4da5ac204e00136f0dabf5605d613a9c5ac045514ee2eae266c89b3994a.
- 16 packaged LKM files: checked against saved independent CI artifact checksums; ABI, KMI and trusted manager certificate checked.
- All 3 packaged ksud executables: exact SHA-256 match to official v3.4.2 release binaries (stripping disabled for these executables).
- Packaged recovery installer: exact source match; sh -n passed.
- Both custom GitHub Actions workflows: actionlint passed.
- Device installation/boot/root testing: not performed.

APK SHA-256: aa7d525578af189e06721d8fa364d07f643bdd0add41d1bf436699edb5a0acf4
