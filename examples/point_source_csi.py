from gate_macro_gen import Application

a = Application()
a.setMatpath("GateMaterials.db")
a.setPhysics("emstandard")
a.setWorld(x = 40, y = 40, z = 80, unit = "cm")
a.addSourceGps(
        "gammas",
        particle = "gamma",
        mono = (662., "keV"),
        activity = (5e5, "becquerel"),
        angle = {"type": "iso"},
        position = {"type": "Volume", "shape": "Cylinder",
                    "radius": (1, "cm"),
                    "halfz": (1, "mm"),
                    "centre": (0, 0, 25, "cm")}
)
a.addRootOutput(
        filename = "output",
        flags = ["Hit", "Singles", "Ntuple", "Singles_crystal",
                 "Singles_crystal_readout"]
)
a.addTreeOutput(
        filenames = ["out.root"],
        hits = True,
        collections = ["Singles"]
)
crystal = {
        "primitive": "box",
        "size": (20, 10, 5, "cm"),
        "position": (0, 0, -20, "cm"),
        "material": "CsITl",
        "attach": 1
}
a.addDaughter("world", "crystal", "scanner", crystal)
a.addSinglesDigi("crystal", "adder",
                 {"positionPolicy": "energyWeightedCentroid"})
a.addSinglesDigi("crystal", "readout", {"setDepth": 1})
a.addSinglesDigi("crystal", "energyResolution",
                 {"fwhm": 0.08, "energyOfReference": (662, "keV")})
a.addSinglesDigi("crystal", "pileup",
                 {"setPileupVolume": "crystal", "setPileup": (4, "us")})
a.setVis({"zoom": 1, "style": "surface", "viewpointThetaPhi": (45, 135),
          "endOfEventAction": "accumulate", "verbose": 2, "axes": True})
a.start()

