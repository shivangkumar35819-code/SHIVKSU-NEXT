# Wild KSU custom release

Architecture: ARM64 only. Android package: com.twj.wksu.
This is a personal build, not an official WildKernels-signed release.

Supported upstream Wild KSU 3.1.1 GKI kernel families:

- android12-5.10
- android13-5.10
- android13-5.15
- android14-5.15
- android14-6.1
- android15-6.6
- android16-6.12

These are kernel KMI families, not a promise about every Android OS version or
OEM kernel. ARM32, x86, non-GKI, 4.x/5.4, and android17-6.18 are not supported.

Each module trusts the exact certificate in manager-cert.der and identity.json.
The APK daemon embeds all seven modules and the rebuilt ksuinit. The loader retries
once only if a new kernelsu kernel log explicitly reports a vermagic mismatch.
Other errors still fail. Changing vermagic does not prove kernel ABI compatibility.

The supplied boot image is based on the user's gold firmware boot image:
OS3.0.4.0.VNQINXM / Android 15. It is not for other firmware or devices.
CI compares the unpacked kernel with stock and compares the embedded module and
init with the built binaries. No allow-shell or unauthenticated-adbd option is set.

For a different boot image, install the custom APK, choose the stock image for
that exact firmware, and use the patch-file option. Its rebuilt daemon selects
the matching bundled module for the detected or explicitly selected kernel KMI.
Unsupported KMIs fail before an image can be produced with a missing module.
Do not reuse the previous official/debug APK with this custom module.

The signing key is unchanged from the previous custom ARM64 build, so this APK
can update that custom build. Before installing over an APK signed with a different key under the same
package must be uninstalled; that removes its local Manager settings.

The .ko file is a kernel module, not a boot image. It must not be flashed directly.
Keep the original stock boot image available for recovery. The user performs any
device flashing and testing; this build process never accesses the phone.

After the user installs the matching APK and boots the matching image, the app
should report Working and expose Superuser controls. Grant a terminal access
and check `su -c id` for uid=0(root). Root success remains unverified until then.

Signing credentials remain outside this repository under the user's local
.android/wild-ksu-release directory. Keep that directory for future APK updates.
