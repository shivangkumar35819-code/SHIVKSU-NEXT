# Wild KSU custom build verification

Date: 2026-10-20 (Asia/Calcutta)
Source: WildKernels/Wild_KSU commit db2fc89899658a4345df3b27a34098a80cc00e2a
Build configuration: private SHIVKSU-NEXT branch wild-ksu-custom-20261020
Binary build run: https://github.com/shivangkumar35819-code/SHIVKSU-NEXT/actions/runs/39336619030

Passed:
- Custom ARM64 module compiled; kernel symbol/version checks passed.
- Three loader regression tests and strict loader Clippy passed.
- ARM64 daemon compile and Clippy passed; Rust formatting checks passed.
- Static ARM64 init has no ELF interpreter dependency.
- Host patcher created the image from the provided gold OS3.0.4.0.VNQINXM stock boot.
- Unpacked patched kernel equals stock; ramdisk init/module equal the built files.
- Downloaded binary checksums match the CI manifest.
- Daemon compressed assets decode to the exact built loader and module.
- Release APK built successfully and passes APK signature verification.
- APK certificate matches module's expected certificate (794 bytes).
- APK uses v2 signing, with no v1/v3 signature; it is not debug-key signed.
- APK is ARM64 only and contains the exact verified daemon.
- Recovery scripts are packaged; recovery shell syntax check passed.

No phone installation, reboot, temporary boot, flashing, or root policy changes
were performed during this custom build. Device root/boot testing remains for
the user. A vermagic retry cannot guarantee compatibility with every kernel ABI.

APK metadata:
package: name='com.twj.wksu' versionCode='33208' versionName='v3.1.1-custom' platformBuildVersionName='16' platformBuildVersionCode='36' compileSdkVersion='36' compileSdkVersionCodename='16'

Public signing identity:
```json
{
  "certificate_size": 794,
  "certificate_sha256": "48d55731b637377701e89dad6f6b54a7c4582444be00648eef681ed6199ef0f2",
  "package": "com.twj.wksu",
  "kmi": "android15-6.6",
  "abi": "arm64-v8a"
}
```
