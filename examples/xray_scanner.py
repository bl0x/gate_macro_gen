from gate_macro_gen import *

a = Application()
a.setMatpath("/home/bloeher/opt/Gate-9.3/GateMaterials.db")
a.setPhysics("emstandard")
a.setWorld(x = 200, y = 200, z = 200, unit = "cm", material = "Air")

e_keV = 120
emin = 1
emax = e_keV
temp = 11606000 * e_keV # 1 eV = 11606 Kelvin
a.add(SourceGps("xray",
                particle = "gamma",
                brem = (emin, emax, "keV", temp),
                activity = (1e3, "becquerel"),
                angle = {"type": "iso", "rot1": (0, 0, 1)},
                position = {"type": "Volume", "shape": "Cylinder",
                            "radius": (2, "mm"),
                            "halfz": (0.1, "mm"),
                            "centre": (-80, -80, 0, "cm")},
                theta = (0, 90, "deg"),
                phi = (-90-1, -90+1, "deg")
))

line = Box(
        name = "line",
        size = (10, 100, 10, "cm"),
        position = (55, 0, 0, "cm"),
        material = "Air",
        color = "cyan",
        repeaters = RingRepeater(
            n = 2,
            modulo = 1,
            rotate = True,
            point1 = (0, 0, 0, "mm"),
            point2 = (0, 0, 1, "mm"),
            angle = (0, 90, "deg")
        )
)
crystal = Box(
        name = "crystal",
        size = (1, 10, 1, "cm"),
        position = (0, 0, 0, "cm"),
        material = "CsITl",
        repeaters = LinearRepeater(
            n = 10,
            vector = (0, 10, 0, "cm")
        ),
        color = "magenta"
)
a.add(Scanner("world", levels=[line,crystal], sensitiveDetector="crystal"))

a.add(SinglesDigi("crystal", "adder",
                 {"positionPolicy": "energyWeightedCentroid"}))
a.add(SinglesDigi("crystal", "readout", {"setDepth": 1}))
a.add(SinglesDigi("crystal", "energyResolution",
                 {"fwhm": 0.08, "energyOfReference": (662, "keV")}))
a.add(SinglesDigi("crystal", "pileup",
                 {"setPileupVolume": "crystal", "setPileup": (4, "us")}))
a.add(SimulationStatisticActor("stats", "stats.txt"))

# Output
a.add(RootOutput(
        filename = "/tmp/xray_scan",
        flags = ["Hit",
                 "Singles",
                 "Ntuple"
                ]
))

a.setVis({"zoom": 1, "style": "wireframe", "viewpointThetaPhi": (0,0),
          "endOfEventAction": "accumulate", "verbose": 1,
          "auxiliaryEdges": False, "axes": True})

print(a.print())