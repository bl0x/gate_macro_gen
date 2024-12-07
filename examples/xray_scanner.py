from gate_macro_gen import *
import argparse

readout_rate_hz = 20
e_keV = 120
belt_speed_cm_s = 20

# Run config

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--visualisation", action="store_true")
parser.add_argument("-b", "--background", action="store_true")
args = parser.parse_args()
do_vis = args.visualisation
do_bg = args.background

# Application


a = Application()
a.setMatpath("/home/bloeher/opt/Gate-9.3/GateMaterials.db")
a.setPhysics("emstandard")
a.setWorld(x = 200, y = 200, z = 200, unit = "cm", material = "Air")
a.setTimeSliceDuration(1.0/readout_rate_hz)
a.setTimeStart(0.5)
a.setTimeStop(0.6)

emin = 1
emax = e_keV
temp = 11606000 * e_keV # 1 eV = 11606 Kelvin
a.add(SourceGps("xray",
                particle = "gamma",
                brem = (emin, emax, "keV", temp),
                activity = (1e8, "becquerel"),
                angle = {"type": "iso", "rot1": (0, 0, 1)},
                position = {"type": "Volume", "shape": "Cylinder",
                            "radius": (2, "mm"),
                            "halfz": (0.1, "mm"),
                            "centre": (-80, -80, 0, "cm")},
                theta = (0, 90, "deg"),
                phi = (-90-1, -90+1, "deg")
))

# High energy scanner
line = Box(
        name = "line",
        size = (1, 160, 1, "cm"),
        position = (86, 0, 0, "cm"),
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
        size = (1, 2.5, 1, "cm"),
        position = (0, 0, 0, "cm"),
        material = "CsITl",
        repeaters = LinearRepeater(
            n = 64,
            vector = (0, 2.5, 0, "cm")
        ),
        color = "magenta"
)
# Low energy scanner
line_le = Box(
        name = "line_le",
        size = (1, 160, 1, "cm"),
        position = (85, 0, 0, "cm"),
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
copper_le = Box(
        name = "copper_le",
        size = (0.2, 160, 1, "cm"),
        position = (0.2, 0, 0, "cm"),
        material = "Copper",
        color = "blue"
)
crystal_le = Box(
        name = "crystal_le",
        size = (0.05, 2.5, 1, "cm"),
        position = (0, 0, 0, "cm"),
        material = "CsI",
        repeaters = LinearRepeater(
            n = 64,
            vector = (0, 2.5, 0, "cm")
        ),
        color = "red"
)
# Absorber
block1 = Box(
        name = "block1",
        size = (10, 1, 10, "cm"),
        position = (-70, 0, -10, "cm"),
        material = "Aluminium",
        color = "yellow",
        motion = Translation(10, 0, belt_speed_cm_s, "cm/s")
)
block2 = Box(
        name = "block2",
        size = (10, 2, 10, "cm"),
        position = (-60, 0, -10, "cm"),
        material = "Aluminium",
        color = "yellow",
        motion = Translation(10, 0, belt_speed_cm_s, "cm/s")
)
block3 = Box(
        name = "block3",
        size = (10, 4, 10, "cm"),
        position = (-50, 0, -10, "cm"),
        material = "Aluminium",
        color = "yellow",
        motion = Translation(10, 0, belt_speed_cm_s, "cm/s")
)
block4 = Box(
        name = "block4",
        size = (10, 0.5, 10, "cm"),
        position = (-40, 0, -10, "cm"),
        material = "Steel",
        color = "yellow",
        motion = Translation(10, 0, belt_speed_cm_s, "cm/s")
)
block5 = Box(
        name = "block5",
        size = (10, 2, 10, "cm"),
        position = (-30, 0, -10, "cm"),
        material = "Plastic",
        color = "yellow",
        motion = Translation(10, 0, belt_speed_cm_s, "cm/s")
)
if do_bg == False:
    a.add(block1);
    a.add(block2);
    a.add(block3);
    a.add(block4);
    a.add(block5);
a.add(Scanner("world", levels=[line,crystal],
              sensitiveDetector="crystal"))
a.add(Scanner("world", levels=[line_le,[crystal_le,copper_le]],
              sensitiveDetector="crystal_le"))

# Digi for HE
a.add(SinglesDigi("crystal", "adder",
                 {"positionPolicy": "energyWeightedCentroid"}))
a.add(SinglesDigi("crystal", "readout", {"setDepth": 1}))
a.add(SinglesDigi("crystal", "energyResolution",
                 {"fwhm": 0.08, "energyOfReference": (662, "keV")}))
a.add(SinglesDigi("crystal", "pileup",
                 {"setPileupVolume": "crystal", "setPileup": (0.01, "us")}))
# Digi for LE
a.add(SinglesDigi("crystal_le", "adder",
                 {"positionPolicy": "energyWeightedCentroid"}))
a.add(SinglesDigi("crystal_le", "readout", {"setDepth": 1}))
a.add(SinglesDigi("crystal_le", "energyResolution",
                 {"fwhm": 0.08, "energyOfReference": (662, "keV")}))
a.add(SinglesDigi("crystal_le", "pileup",
                 {"setPileupVolume": "crystal_le", "setPileup": (0.01, "us")}))
a.add(SimulationStatisticActor("stats", "stats.txt"))

# Output
pre = "/tmp/xray_scan_dual_1e6"
if do_bg == True:
    root_filename = f"{pre}_bg"
    tree_filename = f"{pre}_tree_bg.root"
else:
    root_filename = f"{pre}"
    tree_filename = f"{pre}_tree.root"

a.add(RootOutput(
        filename = root_filename,
        flags = ["Hit",
                 "Singles_crystal",
                 "Singles_crystal_le",
                 "Ntuple"
                ]
))
a.add(TreeOutput(
        filenames = tree_filename,
        hits = True,
        collections = ["Singles"]
))

if do_vis == True:
    a.setVis({"zoom": 1, "style": "wireframe", "viewpointThetaPhi": (0,0),
          "endOfEventAction": "accumulate", "verbose": 1,
          "auxiliaryEdges": False, "axes": True})

print(a.print())
