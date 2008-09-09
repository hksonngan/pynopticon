#!/bin/bash
cd features
make clean
make
cd ../utility
make clean
make
cd ../regcovextract
make clean
make
