#!/bin/bash
export PYTHONPATH=.
mkdir -p test_output
python examples/minimal.py > test_output/test.mac
Gate --qt test_output/test.mac
