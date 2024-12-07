from gate_macro_gen import *
import argparse

# Run config

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--visualisation", action="store_true")
args = parser.parse_args()
do_vis = args.visualisation

# Application

a = Application()
a.setMatpath("GateMaterials.db")
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
a.setTimeSliceDuration(1.0)
a.setTimeStop(1.0)

e = 140
n = 5e6
mat = "CsITl"
thickness = 2.8

if do_vis == True:
    e = 50
    filename = "/tmp/vis"
    statsname = "/tmp/vis.stats"
else:
    _dir = "/tmp/xray_attenuation/"
    pre = f"{_dir}/xray_att_w_{mat}_{thickness}_{e}keV_{int(n)}"
    filename = f"{pre}.root"
    statsname = f"{pre}.stats"

a.setWorld(x = 100, y = 100, z = 100, unit = "cm", material = "Vacuum")
### X-ray source based on simulated spectrum (with electrons)
a.add(SourceGps("x-rays",
        particle = "gamma",
        user_spectrum = "/tmp/hist",
        activity = (n, "becquerel"),
        angle = {"type": "iso"},
        position = {"centre": (0, 0, -25, "cm")}
))

filter = Box("filter",
        size = (200, 200, thickness, "mm"),
        position = (0, 0, 0, "cm"),
        material = mat
)

recorder = Box("recorder",
        size = (20, 20, 1, "cm"),
        position = (0, 0, 5, "cm"),
        material = "Vacuum"
)
a.add(filter)
a.add(recorder)

a.add(SimulationStatisticActor("stats", statsname))
a.add(PhaseSpaceActor("phasespace", filename,
                      attach="recorder"))

if do_vis == True:
    a.setVis({"viewpointThetaPhi": (45, 135), "axes": True,
              "endOfEventAction": "accumulate", "verbose": 1})

print(a.print())
