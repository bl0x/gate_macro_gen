from gate_macro_gen import *

a = Application()
a.setMatpath("/home/bloeher/opt/Gate-9.3/GateMaterials.db")
a.setPhysics("emstandard")
# a.setWorld(x = 200, y = 200, z = 200, unit = "cm", material = "Air")
a.add(SourcePencilBeam("electrons",
                particle = "e-",
                energy = (120, 10, "keV"),
                activity = (1e5, "becquerel"),
                position = (0, 0, 0, "cm"),
                spread = (2, 2, "mm"),
                divergence = (3, 3, "mrad"),
                emittance = (18, 18, "negative", "negative"),
                rotation = {"axis": (1, 0, 0), "angle": (180, "deg")}
))
scatter = Box("scatter",
          size = (20, 20, 5, "cm"),
          position = (0, 0, -25, "cm"),
          rotations = [{"axis": (1, 0, 0), "angle": (45, "deg")}],
          material = "Copper"
)
crystal = Box(
        name = "crystal",
        size = (10, 10, 10, "cm"),
        position = (0, -25, -25, "cm"),
        material = "CsITl"
)
a.add(Scanner("world", levels=[[crystal,scatter]], sensitiveDetector="crystal"))

a.add(SinglesDigi("crystal", "adder",
                 {"positionPolicy": "energyWeightedCentroid"}))
a.add(SinglesDigi("crystal", "readout", {"setDepth": 1}))
a.add(SinglesDigi("crystal", "energyResolution",
                 {"fwhm": 0.08, "energyOfReference": (662, "keV")}))
a.add(SinglesDigi("crystal", "pileup",
                 {"setPileupVolume": "crystal", "setPileup": (4, "us")}))
a.add(SimulationStatisticActor("stats", "stats.txt"))
a.add(FluenceActor("fluence", "/tmp/fluence.mhd",
                   attach = "scatter",
                   size = (20, 20, 5, "cm"),
                   resolution = (1000, 1000, 1),
                   scatter = False
))
# Output
a.add(RootOutput(
        filename = "/tmp/xray_1e4",
        flags = ["Hit",
                 "Singles",
                 "Ntuple"
                ]
))
# a.setVis({"viewpointThetaPhi": (45, 135), "axes": True})

print(a.print())
