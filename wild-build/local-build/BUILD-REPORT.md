# Wild KSU all-supported ARM64 build verification

Date: 2026-10-20 (Asia/Calcutta)
Source: WildKernels/Wild_KSU db2fc89899658a4345df3b27a34098a80cc00e2a
Build: https://github.com/shivangkumar35819-code/SHIVKSU-NEXT/actions/runs/39338310636
Configuration branch: wild-ksu-custom-20261020, commit d744495

Passed checks:
- All seven upstream ARM64 GKI module targets compiled successfully.
- Each module has the matching package, signing certificate hash and kernel family.
- Missing/extra module matrix guard passed; an incomplete matrix was rejected.
- Loader regression tests, strict Clippy, static ARM64 init build and formatting passed.
- ARM64 daemon compile and Clippy passed with all seven modules embedded.
- Local verifier decompressed the exact built loader and all seven modules from the daemon.
- All CI artifact checksums verified.
- APK release build and APK signature verification passed (v2, no v1/v3, non-debug key).
- Packaged daemon equals the verified daemon; APK is ARM64-only.
- APK certificate uses the same persistent release key as the earlier custom build.
- Recovery installer scripts are packaged.
- CI gold boot image kernel equals stock, and its module/loader match the built files.

Supported kernel KMI families:
- android12-5.10
- android13-5.10
- android13-5.15
- android14-5.15
- android14-6.1
- android15-6.6
- android16-6.12

These kernel families do not guarantee root on every OEM kernel or Android OS
version. ARM32, x86, non-GKI and android17-6.18 support is not claimed.
The included boot image is ONLY for gold OS3.0.4.0.VNQINXM; other devices and
firmware need their own exact stock image patched with the APK.
No phone action was performed. Device boot/root testing remains pending.

APK metadata:
package: name='com.twj.wksu' versionCode='33208' versionName='v3.1.1-custom-all' platformBuildVersionName='16' platformBuildVersionCode='36' compileSdkVersion='36' compileSdkVersionCodename='16'
