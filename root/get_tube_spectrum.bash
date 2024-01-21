#!/bin/bash

file=$1
e_mev=$2

root -l root/get_tube_spectrum.C\(\"$file\",$e_mev\)
