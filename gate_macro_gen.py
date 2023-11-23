# base classes

class Actor():
    def __init__(self):
        pass

class Source():
    def __init__(self):
        pass

class Digi():
    def __init__(self):
        pass

class Output():
    def __init__(self):
        pass

class Primitive():
    def __init__(self):
        pass

class System():
    def __init__(self):
        pass

# derived classes

class SimulationStatisticActor(Actor):
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
    def print(self):
        print(f"/gate/actor/addActor SimulationStatisticActor {self.name}")
        print(f"/gate/actor/{self.name}/save {self.filename}")

class DoseActor(Actor):
    def __init__(self, name, filename, attached):
        self.name = name
        self.filename = filename
        self.attached = attached
    def print(self):
        print(f"/gate/actor/addActor DoseActor {self.name}")
        print(f"/gate/actor/{self.name}/save {self.filename}")
        print(f"/gate/actor/{self.name}/attachTo {self.attached}")

class EnergySpectrumActor(Actor):
    def __init__(self, name, filename, attached, spectrum = None, letSpectrum = None, edep = None, eloss = None):
        self.name = name
        self.filename = filename
        self.attached = attached
        self.spectrum = spectrum
        self.letSpectrum = letSpectrum
        self.edep = edep
        self.eloss = eloss
    def print_hprops(self, pre, props, _min, _max, _bins):
        print(f"{pre}/set{_min} {tup2str(props['emin'])}")
        print(f"{pre}/set{_max} {tup2str(props['emax'])}")
        print(f"{pre}/set{_bins} {tup2str(props['bins'])}")
    def print(self):
        print(f"/gate/actor/addActor EnergySpectrumActor {self.name}")
        pre = f"/gate/actor/{self.name}"
        print(f"{pre}/save {self.filename}")
        print(f"{pre}/attachTo {self.attached}")
        if self.spectrum is not None:
            self.print_hprops(f"{pre}/energySpectrum", self.spectrum,
                              "Emin", "Emax", "NumberOfBins")
        if self.letSpectrum is not None:
            print(f"{pre}/enableLETSpectrum true")
            self.print_hprops(f"{pre}/LETSpectrum", self.letSpectrum,
                              "LETmin", "LETmax", "NumberOfBins")
        if self.edep is not None:
            for f in self.edep:
                print(f"{pre}/enable{f}Histo true")
        if self.eloss is not None:
            print(f"{pre}/enableElossHisto true")
            self.print_hprops(f"{pre}/energyLossHisto", self.eloss,
                              "EdepMin", "EdepMax", "NumberOfEdepBins")




class SourceGps(Source):
    def __init__(self, name, **kwargs):
        self.name = name
        self.props = kwargs
    def print(self):
        p = self.props
        pre = f"/gate/source/{self.name}"
        print(f"/gate/source/addSource {self.name} gps")
        if "activity" in p:
            print(f"{pre}/setActivity {tup2str(p['activity'])}")
        pre += "/gps"
        if "particle" in p:
            print(f"{pre}/particle {p['particle']}")
        if "mono" in p:
            print(f"{pre}/ene/mono {tup2str(p['mono'])}")
        if "angle" in p:
            for k,v in p["angle"].items():
                print(f"{pre}/ang/{k} {tup2str(v)}")
        if "position" in p:
            for k,v in p["position"].items():
                print(f"{pre}/pos/{k} {tup2str(v)}")


class SinglesDigi(Digi):
    def __init__(self, source, name, props):
        self.source = source
        self.name = name
        self.props = props
    def print(self):
        pre = f"/gate/digitizerMgr/{self.source}/SinglesDigitizer/Singles"
        print(f"{pre}/insert {self.name}")
        for k,v in self.props.items():
            print(f"{pre}/{self.name}/{k} {tup2str(v)}")

class Scanner(System):
    def __init__(self, parent, primitive, attach = 0):
        self.parent = parent
        self.primitive = primitive
        self.attach = attach
    def print(self):
        pre = f"/gate/{self.parent}/daughters"
        p = self.primitive
        print(f"{pre}/name {p.name}")
        print(f"{pre}/systemType scanner")
        print(f"{pre}/insert {p.geo}")
        p.print()
        if self.attach > 0:
            print(f"/gate/systems/{p.name}/level{self.attach}/attach {p.name}")
            print(f"/gate/{p.name}/attachCrystalSD")

class Box(Primitive):
    def __init__(self, name, size, position, material):
        self.geo = "box"
        self.name = name
        self.size = size
        self.position = position
        self.material = material
    def print(self):
        pre = f"/gate/{self.name}"
        print(f"{pre}/setMaterial {self.material}")
        print(f"{pre}/placement/setTranslation {tup2str(self.position)}")
        s = self.size
        pre = f"/gate/{self.name}/geometry"
        print(f"{pre}/setXLength {s[0]} {s[3]}")
        print(f"{pre}/setYLength {s[1]} {s[3]}")
        print(f"{pre}/setZLength {s[2]} {s[3]}")

class RootOutput(Output):
    def __init__(self, filename, flags):
        self.filename = filename
        self.flags = flags
    def print(self):
        pre = "/gate/output/root"
        print(f"{pre}/enable")
        print(f"{pre}/setFileName {self.filename}")
        for f in self.flags:
            print(f"{pre}/setRoot{f}Flag 1")

class TreeOutput(Output):
    def __init__(self, filenames, hits, collections):
        self.filenames = filenames
        self.hits = hits
        self.collections = collections
    def print(self):
        pre = "/gate/output/tree"
        print(f"{pre}/enable")
        for f in self.filenames:
            print(f"{pre}/addFileName {f}")
        if self.hits is not None:
            print(f"{pre}/hits/enable")
        for c in self.collections:
            print(f"{pre}/addCollection {c}")

# main application class

class Application:
    def __init__(self):
        self.sources = []
        self.daughters = []
        self.outputs = []
        self.digis = []
        self.actors = []
        self.world = {"x": 0, "y": 0, "z": 0, "unit": None}
        self.matpath = None
        self.physics = "emstandard"
        self.vis = None

    def setMatpath(self, path):
        self.matpath = path

    def setPhysics(self, physics):
        self.physics = physics

    def setWorld(self, x, y, z, unit):
        self.world["x"] = x
        self.world["y"] = y
        self.world["z"] = z
        self.world["unit"] = unit

    def setVis(self, props):
        self.vis = props

    def add(self, something):
        if isinstance(something, Output):
            self.outputs.append(something)
        if isinstance(something, System):
            self.daughters.append(something)
        if isinstance(something, Digi):
            self.digis.append(something)
        if isinstance(something, Source):
            self.sources.append(something)
        if isinstance(something, Actor):
            self.actors.append(something)

    def print(self):
        self.print_mat()
        self.print_phys()
        self.print_world()
        self.print_daughters()
        self.print_actors()
        self.print_digis()
        self.print_init()
        self.print_sources()
        self.print_outputs()
        self.print_vis()
        self.print_start()

    def print_actors(self):
        print("\n# Actors\n")
        for a in self.actors:
            a.print()

    def print_vis(self):
        print("\n# Visualization\n")
        if self.vis is None:
            return
        print(f"/vis/open OGLSQt")
        print(f"/vis/viewer/reset")
        print(f"/vis/drawVolume")
        print(f"/vis/scene/add/hits")
        print(f"/tracking/storeTrajectory 1")
        print(f"/vis/scene/add/trajectories")
        print(f"/gate/application/setTotalNumberOfPrimaries 100")
        for k,v in self.vis.items():
            if k in ["style", "viewpointThetaPhi"]:
                pre = "/vis/viewer/set"
            elif k in ["zoom"]:
                pre = "/vis/viewer"
            elif k in ["endOfEventAction"]:
                pre = "/vis/scene"
            elif k in ["axes"]:
                if v is True:
                    print(f"/vis/scene/add/axes")
                continue
            else:
                pre = "/vis/"
            print(f"{pre}/{k} {tup2str(v)}")

    def print_mat(self):
        mat = f"{self.matpath}"
        print(f"/gate/geometry/setMaterialDatabase {mat}")

    def print_phys(self):
        print("\n# Physics\n")
        print(f"/gate/physics/addPhysicsList {self.physics}")

    def print_world(self):
        print("\n# World\n")
        u = self.world["unit"]
        print(f"/gate/world/geometry/setXLength {self.world['x']} {u}")
        print(f"/gate/world/geometry/setYLength {self.world['y']} {u}")
        print(f"/gate/world/geometry/setZLength {self.world['z']} {u}")

    def print_outputs(self):
        print("\n# Outputs\n")
        for o in self.outputs:
            o.print()

    def print_daughters(self):
        print("\n# Volumes\n")
        for d in self.daughters:
            d.print()

    def print_digis(self):
        print("\n# Digitizers\n")
        for d in self.digis:
            d.print()

    def print_sources(self):
        print("\n# Sources\n")
        for s in self.sources:
            s.print()

    def print_init(self):
        print("\n# Init\n")
        print("/gate/run/initialize")

    def print_start(self):
        print("\n# Start\n")
        print("/gate/random/setEngineName MersenneTwister")
        print("/gate/random/setEngineSeed auto")
        print("/gate/application/startDAQ")

# utilities

def tup2str(tup):
    if isinstance(tup, tuple):
        return " ".join(map(str,(tup)))
    else:
        return str(tup)

