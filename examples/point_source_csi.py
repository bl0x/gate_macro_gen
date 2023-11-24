from gate_macro_gen import Application, RootOutput, TreeOutput, Box, Scanner, SinglesDigi, SourceGps, SimulationStatisticActor, DoseActor, EnergySpectrumActor

a = Application()
a.setWorld(x = 40, y = 40, z = 80, unit = "cm")
a.setMatpath("GateMaterials.db")
a.add(SourceGps(
        "gammas",
        particle = "gamma",
        mono = (662., "keV"),
        activity = (5e1, "becquerel"),
        angle = {"type": "iso"},
        position = {"type": "Volume", "shape": "Cylinder",
                    "radius": (1, "cm"),
                    "halfz": (1, "mm"),
                    "centre": (0, 0, 25, "cm")}
))
a.add(RootOutput(
        filename = "output",
        flags = ["Hit", "Singles", "Ntuple", "Singles_crystal",
                 "Singles_crystal_readout"]
))
a.add(TreeOutput(
        filenames = ["out.root"],
        hits = True,
        collections = ["Singles"]
))
crystal = Box(
        name = "crystal",
        size = (20, 10, 5, "cm"),
        position = (0, 0, -20, "cm"),
        material = "CsITl"
)
a.add(Scanner("world", levels=[crystal], sensitiveDetector="crystal"))
a.add(SinglesDigi("crystal", "adder",
                 {"positionPolicy": "energyWeightedCentroid"}))
a.add(SinglesDigi("crystal", "readout", {"setDepth": 1}))
a.add(SinglesDigi("crystal", "energyResolution",
                 {"fwhm": 0.08, "energyOfReference": (662, "keV")}))
a.add(SinglesDigi("crystal", "pileup",
                 {"setPileupVolume": "crystal", "setPileup": (4, "us")}))
a.add(SimulationStatisticActor("stats", "stats.txt"))
a.add(DoseActor("dose", "dose.mhd", "crystal"))
a.add(EnergySpectrumActor(
    "energy", "energy.root", "crystal",
    spectrum = {"emin": (0, "keV"),
                "emax": (3, "MeV"),
                "bins": 2048},
    letSpectrum = {"emin": (0, "keV/um"),
                   "emax": (100, "keV/um"),
                   "bins": 1000},
    edep = ["Edep", "EdepTime", "EdepTrack", "EdepStep"],
    eloss = {"emin": (0, "keV"),
             "emax": (3, "MeV"),
             "bins": 1024}
))
a.setVis({"zoom": 1, "style": "surface", "viewpointThetaPhi": (45, 135),
          "endOfEventAction": "accumulate", "verbose": 2, "axes": True})
a.print()

