#!/bin/bash

file=$1
e_mev=$2

root -l root/get_attenuation_spectrum.C\(\"$file\",$e_mev\)
