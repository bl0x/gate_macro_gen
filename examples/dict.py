#!/usr/bin/env python3

from gate_macro_gen import *
import json
import yaml
import sys

box = Box(
        name = "crystal",
        size = (20, 10, 5, "cm"),
        position = (0, 0, -20, "cm"),
        material = "CsITl"
        )

if len(sys.argv) < 2:
    print(f"usage: python {sys.argv[0]} json|yaml")
    exit(1)

if sys.argv[1] == "json":
    print(json.dumps(box.dict()))
else:
    print(yaml.dump(box.dict()))
