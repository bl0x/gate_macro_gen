# gate_macro_gen - A generator for openGATE macro files, written in Python

This is a macro file generator for the Monte-Carlo particle simulation tool [https://github.com/OpenGATE](openGate).

**Note:** This tool is meant for the C++ based version of openGate (or simply [https://github.com/OpenGATE/Gate](Gate)). It is not meant for the new Python-based version that is in active development.

## Works with:

* Geant4 9.11.2
* Gate 9.4

## Tested with:

* Geant4 9.10
* Gate 9.3

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

## Testing

Use the `test.bash` script to run a quick test with the `minimal.py` example.

## Geometry export

Specifying `a.vis_type = "VTK"` in the above example uses the VTK visualisation engine of Geant4 (if compiled in). The constructed geometry is then exported as `scene_vtk.gltf` in the popular GLTF format. An additional export is done after running the simulation, to also visualize the trajectories. This file is called `scene_trajectories.gltf`.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.


## Authors:

* **Bastian Löher** - *Initial work*
