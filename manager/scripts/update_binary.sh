#!/bin/sh

TMPDIR="/dev/tmp/shivksu-installer-$$"
mkdir -p "$TMPDIR" 2>/dev/null || exit 1
trap 'rm -rf "$TMPDIR"' EXIT

ARCH="$(getprop ro.product.cpu.abi)"
OUTFD=/proc/self/fd/$2

ui_print() {
  echo -e "ui_print $1\nui_print" >> $OUTFD
}

case "$ARCH" in
    arm64-v8a|x86_64) ;;
    *)
        ui_print "- Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# Extract ksud
unzip -o "$3" "lib/$ARCH/libksud.so" -d "$TMPDIR" >&2 || exit 1

KSUD="$TMPDIR/lib/$ARCH/libksud.so"

chmod 755 "$KSUD"

run_ksud() {
    "$KSUD" "$@" > "$TMPDIR/install.log" 2>&1
    result=$?
    while IFS= read -r line || [ -n "$line" ]; do
        ui_print "$line"
    done < "$TMPDIR/install.log"
    return "$result"
}

# use ksud to install or uninstall
case "$3" in
  *uninstall*|*Uninstall*)
    ui_print "- Uninstalling SHIVKSU-NEXT..."
    run_ksud uninstall
    ;;
  *)
    ui_print "- Installing SHIVKSU-NEXT..."
    KMI="$("$KSUD" boot-info current-kmi)" || exit 1
    case "$KMI" in
        android12-5.10|android13-5.10|android13-5.15|android14-5.15|android14-6.1|android15-6.6|android16-6.12|android17-6.18) ;;
        *)
            ui_print "- No compatible SHIVKSU-NEXT driver for $KMI ($ARCH)"
            exit 1
            ;;
    esac
    LKM="$TMPDIR/kernelsu.ko"
    if ! unzip -p "$3" "assets/custom-lkm/$ARCH/${KMI}_kernelsu.ko" > "$LKM"; then
        ui_print "- Matching SHIVKSU-NEXT driver is missing"
        exit 1
    fi
    run_ksud boot-patch --flash --kmi "$KMI" --module "$LKM"
    ;;
esac

exit $?
