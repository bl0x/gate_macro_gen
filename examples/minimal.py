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
print(a.print())

