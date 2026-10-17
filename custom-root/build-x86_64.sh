#!/usr/bin/env bash
set -euo pipefail

make clean

echo "=== Preparing KDIR for x64 ==="

mkdir -p /opt/ddk/kdir-x64
unset ARCH
unset CROSS_COMPILE
export ARCH=x86_64
kmi=$KMI
pushd /opt/ddk/src/$kmi
export KDIR=/opt/ddk/kdir-x64/$kmi

# ddk-min images contain the source tarball, whose modpost patch is
# not applied to the fresh x86 kdir.  Keep the patch idempotent so
# this also works when the image already contains one or more fixes.
MODPOST=scripts/mod/modpost.c
sed -i -E 's/^([[:space:]]*)check_exports\(mod\);/\1\/\/ check_exports(mod);/' "$MODPOST"
sed -i -E 's/^([[:space:]]*)s->module = exp->module;/\1\/\/ s->module = exp->module;/' "$MODPOST"
sed -i 's/^static void check_exports(/static void __attribute__((unused)) check_exports(/' "$MODPOST"
sed -i 's/__version_ext_names\\") =\\n/__version_ext_names\\") = \\"\\"\\n/' "$MODPOST"

make O=$KDIR gki_defconfig
scripts/config --file $KDIR/.config -d LTO_CLANG -e LTO_NONE -d LTO_CLANG_THIN -d LTO_CLANG_FULL -d THINLTO
if [ "$kmi" == "android16-6.12" ] || [ "$kmi" == "android17-6.18" ]; then
    scripts/config --file $KDIR/.config -e CONFIG_CFI_ICALL_NORMALIZE_INTEGERS
fi
make O=$KDIR modules_prepare
# Generate SELinux headers through Kbuild in this x86 output tree.
make O=$KDIR security/selinux/built-in.a
popd

echo "=== Building x64 kernelsu.ko for KMI: $KMI ==="

EXTRA_ARGS=""
if [ -n "$MANAGER_PACKAGE" ]; then
  EXTRA_ARGS="$EXTRA_ARGS KSU_MANAGER_PACKAGE=$MANAGER_PACKAGE"
fi
if [ -n "$MANAGER_SIZE" ]; then
  EXTRA_ARGS="$EXTRA_ARGS KSU_NEXT_MANAGER_SIZE=$MANAGER_SIZE"
fi
if [ -n "$MANAGER_HASH" ]; then
  EXTRA_ARGS="$EXTRA_ARGS KSU_NEXT_MANAGER_HASH=$MANAGER_HASH"
fi

MDIR=$(realpath .)

if [ "$kmi" == "android17-6.18" ]; then
  make -C $KDIR M=$MDIR MO=$MDIR compile_commands.json modules CONFIG_KSU=m CONFIG_KSU_X86_PATCH_SYSCALL_DISPATCHER=y $EXTRA_ARGS
else
  make -C $KDIR M=$MDIR src=$MDIR compile_commands.json modules CONFIG_KSU=m CONFIG_KSU_X86_PATCH_SYSCALL_DISPATCHER=y $EXTRA_ARGS
fi

echo "=== Build completed ==="

# Create output directory in GitHub workspace
OUT_DIR="$GITHUB_WORKSPACE/out/x86_64"
mkdir -p $OUT_DIR

# Copy with KMI-specific naming
OUTPUT_NAME="$KMI_kernelsu.ko"
cp kernelsu.ko "$OUT_DIR/$OUTPUT_NAME"

echo "Copied to: $OUT_DIR/$OUTPUT_NAME"
ls -la "$OUT_DIR/$OUTPUT_NAME"
echo "Size: $(du -h "$OUT_DIR/$OUTPUT_NAME" | cut -f1)"
llvm-strip -d "$OUT_DIR/$OUTPUT_NAME"
echo "Size after stripping: $(du -h "$OUT_DIR/$OUTPUT_NAME" | cut -f1)"

