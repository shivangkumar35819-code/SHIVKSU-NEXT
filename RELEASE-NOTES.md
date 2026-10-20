SHIVKSU NEXT v3.4.2-shiv.1 (33356), based on KernelSU-Next v3.4.2.

- App label and home title: SHIVKSU NEXT.
- Includes 16 custom LKM drivers: ARM64 and x86_64 across eight GKI KMIs (Android 12/5.10 through Android 17/6.18; see README).
- Matching custom driver selected for boot-image patching and recovery installation.
- Signed with the existing local manager key; packaged drivers authenticate the same certificate.
- Source, driver rebuild workflow, APK build workflow and checksums included.

Validation: release build, APK signing identity, all 16 ELF driver identities/KMIs/checksums, official daemon hashes, app label and installer shell syntax.

Device boot/root testing has not been performed. This is not universal root support. Installing the APK alone does not install the kernel driver. The separate driver ZIP is not a flashable ZIP or boot image. Use the exact firmware boot image for your device.
