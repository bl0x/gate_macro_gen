from gate_macro_gen import *
import argparse

# Run config

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--visualisation", action="store_true")
args = parser.parse_args()
do_vis = args.visualisation

# Application

a = Application()
a.setMatpath("/home/bloeher/opt/Gate-9.3/GateMaterials.db")
a.setPhysics("emstandard_opt4")
a.set("/process/em/deexcitationIgnoreCut true")
a.set("/process/em/fluo true")
a.set("/process/em/pixe true")
a.set("/process/em/auger true")
a.set("/process/em/pixeXSmodel ECPSSR_ANSTO")
a.set("/process/em/fluoANSTO true")
a.set("/process/em/augerCascade true")
a.set("/process/em/lowestElectronEnergy 10 eV")
a.set("/run/setCut 2 um")
a.set("/run/setCutForAGivenParticle gamma 0.5 um")
a.set("/process/em/verbose 0")
a.set("/process/em/printParameters")
a.setTimeSliceDuration(10.0)
a.setTimeStop(10.0)

e = 160
n = 1e6
if do_vis == True:
    e = 50
    filename = "/tmp/vis"
    statsname = "/tmp/vis.stats"
else:
    pre = f"/tmp/xray_tube_Gps_w_spectrum_Cu200u_{e}keV_{n}"
    filename = pre
    statsname = f"{pre}.stats"

# a.setWorld(x = 100, y = 100, z = 100, unit = "cm", material = "Air")
### Test source for gammas
#a.add(SourceGps("gammas",
#        particle = "gamma",
#        mono = (160., "keV"),
#        activity = (n, "becquerel"),
#        angle = {"type": "iso"},
#        position = {"centre": (0, -20, 0, "cm")}
#))
### This source does not produce a realistic X-Ray spectrum
# e_keV = e
# emin = 1
# emax = e_keV
# temp = 1160600 * e_keV # 1 eV = 11606 Kelvin
# a.add(SourceGps("xray",
#                 particle = "gamma",
#                 brem = (emin, emax, "keV", temp),
#                 activity = (n, "becquerel"),
#                 angle = {"type": "iso", "rot1": (0, 0, 1)},
#                 position = {"type": "Volume", "shape": "Cylinder",
#                             "radius": (0.5, "mm"),
#                             "halfz": (0.1, "mm"),
#                             "centre": (0, -8, -23, "cm")},
#                 theta = (-90-5, 90+5, "deg"),
#                 phi = (90-5, 90+5, "deg")
# ))
### X-ray source based on simulated spectrum (with electrons)
a.add(SourceGps("x-rays",
        particle = "gamma",
        user_spectrum = "/tmp/hist",
        activity = (n, "becquerel"),
        angle = {"type": "iso"},
        position = {"centre": (0, 0, -25, "cm")}
))
### Electron beam source
#a.add(SourcePencilBeam("electrons",
#                particle = "e-",
#                energy = (e, 10, "keV"),
#                activity = (n, "becquerel"),
#                position = (0, 0, 0, "cm"),
#                spread = (2, 2, "mm"),
#                divergence = (3, 3, "mrad"),
#                emittance = (18, 18, "negative", "negative"),
#                rotation = {"axis": (1, 0, 0), "angle": (180, "deg")}
#))
#scatter = Box("scatter",
#          size = (20, 20, 5, "cm"),
#          position = (0, 0, -25, "cm"),
#          rotations = [{"axis": (1, 0, 0), "angle": (45, "deg")}],
#          material = "Tungsten"
#)

crystal = Box(
        name = "crystal",
        size = (10, 2, 10, "cm"),
        position = (0, -25, -25, "cm"),
        material = "CsITl"
)
filter = Box(
        name = "filter",
        size = (100, 0.2, 100, "mm"),
        position = (0, -10, -25, "cm"),
        material = "Copper"
)
a.add(Scanner("world", levels=[[crystal,filter]],
              sensitiveDetector="crystal"))

a.add(SinglesDigi("crystal", "adder",
                 {"positionPolicy": "energyWeightedCentroid"}))
a.add(SinglesDigi("crystal", "readout", {"setDepth": 1}))
a.add(SinglesDigi("crystal", "energyResolution",
                 {"fwhm": 0.001, "energyOfReference": (100, "keV")}))
# a.add(SinglesDigi("crystal", "pileup",
#                 {"setPileupVolume": "crystal", "setPileup": (0.001, "us")}))
a.add(SimulationStatisticActor("stats", statsname))
# a.add(FluenceActor("fluence", "/tmp/fluence.mhd",
#                    attach = "scatter",
#                    size = (20, 20, 5, "cm"),
#                    resolution = (1000, 1000, 1),
#                    scatter = False
# ))
# Output
a.add(RootOutput(
        filename = filename,
        flags = ["Singles",
                 "Ntuple"
                ]
))

if do_vis == True:
    a.setVis({"viewpointThetaPhi": (45, 135), "axes": True,
              "endOfEventAction": "accumulate", "verbose": 1})

print(a.print())
