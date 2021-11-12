#!/bin/bash

DIR=$(dirname "$0")

cd "$DIR"

PREFIX=$(pwd)/root
NVIM="$PREFIX/bin/nvim"

mkdir build

rm -rf root
mkdir root

# Building

cmake \
  -Bbuild \
  -GNinja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_INSTALL_PREFIX=$PREFIX \
  -DUSE_BUNDLED=OFF \
  ..

ninja -C build
ninja -C build install

# Testing

rm transcript.txt

sleep 1

expect -c "
spawn -noecho $NVIM -u init.vim test.pas;
sleep 1; 
send \"jjjoFoobar\33\"; 
sleep 1; 
send \"yyppp\r\33\"; 
sleep 1; 
send \":q!\r\"; 
sleep 1; 
interact;
sleep 1; 
"

sleep 1

grep 'contentChanges' transcript.txt
