#!/usr/bin/bash
## compares two tar.gz archives for equality of contents, even if
## files were added in different orders/different compression params
## were used

set -Eeuo pipefail

function errorhandle() {
    exit 2;
}

function cleanup() {
    rm -r "$folder1";
    rm -r "$folder2";
}

trap cleanup EXIT SIGINT;
trap errorhandle ERR;

folder1=$(mktemp -d);
folder2=$(mktemp -d);

cp -r "$1" "$folder1"/x.tar.gz;
cp -r "$2" "$folder2"/x.tar.gz;

# extract and remove archives
cd "$folder1";
tar -xzf "$folder1"/x.tar.gz;
rm x.tar.gz;

cd "$folder2";
tar -xzf "$folder2"/x.tar.gz;
rm x.tar.gz;

#compare
thediff=$(diff -qr "$folder1" "$folder2") || true;
if [[ -n "$thediff" ]];
then
    echo "$thediff";
    exit 1
fi;
