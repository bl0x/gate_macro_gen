# gate_macro_gen - A generator for openGATE macro files, written in Python

This is a macro file generator for the Monte-Carlo particle simulation tool openGate.

## Why?

openGATE macro files are listings of commands to the internal processing engine, so essentially RPC calls. Due to the modular nature of openGATE (or GEANT4, for that matter), the format of the macro files is highly repetitive.

The idea of this project is to remove the redundant parts of the macro file and instead add the possibility to use Python language features (such as loops and simple arithmetic).

As an example, the generator expands the following code to a ~100 line macro file, ready to run a full openGATE simulation.

```python
from gate_macro_gen import *

a = Application()
a.add(SourceGps("gammas",
        particle = "gamma",
        mono = (662., "keV"),
        activity = (1e3, "becquerel"),
        angle = {"type": "iso"},
        position = {"centre": (0, 0, 25, "cm")}
))
crystal = Box(
        name = "crystal",
        size = (10, 10, 10, "cm"),
        position = (0, 0, -25, "cm"),
        material = "CsITl"
)
a.add(Scanner("world", levels=[crystal], sensitiveDetector="crystal"))
a.add(SimulationStatisticActor("stats", "stats.txt"))
a.setVis({"zoom": 1, "style": "surface", "viewpointThetaPhi": (45, 135),
          "endOfEventAction": "accumulate", "axes": True})
a.print()
```

Use this command to directly run the simulation:

```bash
python examples/minimal.py > /tmp/macro && Gate --qt /tmp/macro
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.


## Authors:

* **Bastian Löher** - *Initial work*
