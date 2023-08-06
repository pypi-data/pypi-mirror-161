#!/usr/bin/env bash

# Execute to build all Rivet routines in this directory
cd $CONTUR_DATA_PATH/data/Rivet
rm -f *.so
if [ `ls -1 *.cc 2>/dev/null | wc -l ` -gt 0 ]; then
    rivet-build Rivet-ConturOverload.so --std=c++14 *.cc
fi
