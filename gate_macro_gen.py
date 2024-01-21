# base classes

class Actor():
    def __init__(self):
        pass

class Repeater():
    def __init__(self):
        pass

class Translation():
    def __init__(self, x, y, z, unit):
        self.x = x
        self.y = y
        self.z = z
        self.unit = unit
    def print(self, parent):
        text = f"/gate/{parent}/moves/insert translation\n"
        speed = f"{self.x} {self.y} {self.z} {self.unit}"
        text += f"/gate/{parent}/translation/setSpeed {speed}\n"
        return text

class Source():
    def __init__(self, name, **kwargs):
        self.name = name
        self.props = kwargs
    def print(self):
        p = self.props
        pre = f"/gate/source/{self.name}"
        text = ""
        if "activity" in p:
            text += f"{pre}/setActivity {tup2str(p['activity'])}\n"
        return text

class Digi():
    def __init__(self):
        pass

class Output():
    def __init__(self):
        pass

class Primitive():
    def __init__(self, name, parent, geo, material, position, rotations=None,
                 color=None, repeaters=None, motion=None):
        self.name = name
        self.parent = parent
        self.geo = geo
        self.position = position
        self.rotations = rotations
        self.material = material
        self.color = color
        self.repeaters = repeaters
        self.motion = motion
    def print(self):
        pre = f"/gate/{self.name}"
        text = f"{pre}/setMaterial {self.material}\n"
        if self.color is not None:
            text += f"{pre}/vis/setColor {self.color}\n"
        pre = f"/gate/{self.name}/placement"
        if self.rotations is not None:
            for r in self.rotations:
                text += f"{pre}/setRotationAxis {tup2str(r['axis'])}\n"
                text += f"{pre}/setRotationAngle {tup2str(r['angle'])}\n"
        text += f"{pre}/setTranslation {tup2str(self.position)}\n"
        if self.repeaters is not None:
            if isinstance(self.repeaters, list):
                for r in self.repeaters:
                    text += r.print(self.name)
            else:
                text += self.repeaters.print(self.name)
        if self.motion is not None:
            if isinstance(self.motion, list):
                for m in self.motion:
                    text += m.print(self.name)
            else:
                text += self.motion.print(self.name)
        return text
    def dict(self):
        return {"name": self.name,
                "material": self.material,
                "position": self.position,
                "rotations": self.rotations}

class System():
    def __init__(self):
        pass

# derived classes

class SimulationStatisticActor(Actor):
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
    def print(self):
        text = f"/gate/actor/addActor SimulationStatisticActor {self.name}\n"
        text += f"/gate/actor/{self.name}/save {self.filename}\n"
        return text

class PhaseSpaceActor(Actor):
    def __init__(self, name, filename, **kwargs):
        self.name = name
        self.filename = filename
        self.props = kwargs
    def print(self):
        text = f"/gate/actor/addActor PhaseSpaceActor {self.name}\n"
        pre = f"/gate/actor/{self.name}"
        text += f"{pre}/save {self.filename}\n"
        p = self.props
        if "attach" in p:
            text += f"{pre}/attachTo    {p['attach']}\n"
        return text

class FluenceActor(Actor):
    def __init__(self, name, filename, **kwargs):
        self.name = name
        self.filename = filename
        self.props = kwargs
    def print(self):
        text = f"/gate/actor/addActor FluenceActor {self.name}\n"
        pre = f"/gate/actor/{self.name}"
        text += f"{pre}/save {self.filename}\n"
        text += f"{pre}/stepHitType pre\n"
        p = self.props
        if "attach" in p:
            text += f"{pre}/attachTo      {p['attach']}\n"
        if "size" in p:
            text += f"{pre}/setSize       {tup2str(p['size'])}\n"
        if "resolution" in p:
            text += f"{pre}/setResolution {tup2str(p['resolution'])}\n"
        if "scatter" in p:
            enable = "true" if p['scatter'] == True else "false"
            text += f"{pre}/enableScatter {enable}\n"
        return text

class DoseActor(Actor):
    def __init__(self, name, filename, attached):
        self.name = name
        self.filename = filename
        self.attached = attached
    def print(self):
        text = f"/gate/actor/addActor DoseActor {self.name}\n"
        text += f"/gate/actor/{self.name}/save {self.filename}\n"
        text += f"/gate/actor/{self.name}/attachTo {self.attached}\n"
        return text

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
        text = f"{pre}/set{_min} {tup2str(props['emin'])}\n"
        text += f"{pre}/set{_max} {tup2str(props['emax'])}\n"
        text += f"{pre}/set{_bins} {tup2str(props['bins'])}\n"
        return text
    def print(self):
        text = f"/gate/actor/addActor EnergySpectrumActor {self.name}\n"
        pre = f"/gate/actor/{self.name}"
        text += f"{pre}/save {self.filename}\n"
        text += f"{pre}/attachTo {self.attached}\n"
        if self.spectrum is not None:
            text += self.print_hprops(f"{pre}/energySpectrum", self.spectrum,
                              "Emin", "Emax", "NumberOfBins")
        if self.letSpectrum is not None:
            text += f"{pre}/enableLETSpectrum true\n"
            text += self.print_hprops(f"{pre}/LETSpectrum", self.letSpectrum,
                              "LETmin", "LETmax", "NumberOfBins")
        if self.edep is not None:
            for f in self.edep:
                text += f"{pre}/enable{f}Histo true\n"
        if self.eloss is not None:
            text += "{pre}/enableElossHisto true\n"
            text += self.print_hprops(f"{pre}/energyLossHisto", self.eloss,
                              "EdepMin", "EdepMax", "NumberOfEdepBins")
        return text

class LinearRepeater(Repeater):
    def __init__(self, **kwargs):
        self.props = kwargs
    def print(self, parent):
        p = self.props
        pre = f"/gate/{parent}/linear"
        text = f"/gate/{parent}/repeaters/insert linear\n"
        text += f"{pre}/setRepeatNumber {p['n']}\n"
        text += f"{pre}/setRepeatVector {tup2str(p['vector'])}\n"
        return text

class RingRepeater(Repeater):
    def __init__(self, **kwargs):
        self.props = kwargs
    def print(self, parent):
        p = self.props
        pre = f"/gate/{parent}/ring"
        text = f"/gate/{parent}/repeaters/insert ring\n"
        text += f"{pre}/setRepeatNumber {p['n']}\n"
        text += f"{pre}/setModuloNumber {p['modulo']}\n"
        text += f"{pre}/setPoint1 {tup2str(p['point1'])}\n"
        text += f"{pre}/setPoint2 {tup2str(p['point2'])}\n"
        a, da, u = p['angle']
        text += f"{pre}/setFirstAngle {a} {u}\n"
        text += f"{pre}/setAngularSpan {da} {u}\n"
        rotate = "enable" if p['rotate'] == True else "disable"
        text += f"{pre}/{rotate}AutoRotation\n"
        return text

class QuadrantRepeater(Repeater):
    def __init__(self, **kwargs):
        self.props = kwargs
    def print(self, parent):
        p = self.props
        pre = f"/gate/{parent}/quadrant"
        text = f"/gate/{parent}/repeaters/insert quadrant\n"
        text += f"{pre}/setLineNumber {p['lines']}\n"
        text += f"{pre}/setOrientation {tup2str(p['orientation'])}\n"
        text += f"{pre}/setCopySpacing {tup2str(p['spacing'])}\n"
        text += f"{pre}/setMaxRange {tup2str(p['range'])}\n"
        return text

class SourcePencilBeam(Source):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    def print(self):
        pre = f"/gate/source/{self.name}"
        text = f"/gate/source/addSource {self.name} PencilBeam\n"
        text += super().print()
        p = self.props
        if "particle" in p:
            text += f"{pre}/setParticleType {p['particle']}\n"
        if "energy" in p:
            e, de, ue = p['energy']
            text += f"{pre}/setEnergy      {e} {ue}\n"
            text += f"{pre}/setSigmaEnergy {de} {ue}\n"
        if "position" in p:
                text += f"{pre}/setPosition {tup2str(p['position'])}\n"
        if "spread" in p:
                dx, dy, u = p['spread']
                text += f"{pre}/setSigmaX {dx} {u}\n"
                text += f"{pre}/setSigmaY {dy} {u}\n"
        if "rotation" in p:
                r = p['rotation']
                text += f"{pre}/setRotationAxis  {tup2str(r['axis'])}\n"
                text += f"{pre}/setRotationAngle {tup2str(r['angle'])}\n"
        if "divergence" in p:
                theta, phi, u = p['divergence']
                text += f"{pre}/setSigmaTheta {theta} {u}\n"
                text += f"{pre}/setSigmaPhi   {phi} {u}\n"
        if "emittance" in p:
                theta, phi, t_norm, p_norm = p['emittance']
                u = "mm*mrad"
                text += f"{pre}/setEllipseXThetaEmittance    {theta} {u}\n"
                text += f"{pre}/setEllipseXThetaRotationNorm {t_norm} {u}\n"
                text += f"{pre}/setEllipseYPhiEmittance      {phi} {u}\n"
                text += f"{pre}/setEllipseYPhiRotationNorm   {p_norm} {u}\n"
        return text


class SourceGps(Source):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    def print(self):
        pre = f"/gate/source/{self.name}"
        text = f"/gate/source/addSource {self.name} gps\n"
        text += super().print()
        p = self.props
        pre += "/gps"
        if "particle" in p:
            text += f"{pre}/particle {p['particle']}\n"
        if "mono" in p:
            text += f"{pre}/ene/mono {tup2str(p['mono'])}\n"
        if "user_spectrum" in p:
            text += f"{pre}/ene/type UserSpectrum\n"
            text += f"{pre}/setSpectrumFile {p['user_spectrum']}\n"
        if "brem" in p:
            emin, emax, unit, temp = p['brem']
            text += f"{pre}/ene/type Brem\n"
            text += f"{pre}/ene/min {emin} {unit}\n"
            text += f"{pre}/ene/max {emax} {unit}\n"
            text += f"{pre}/ene/temp {temp}\n"
        if "angle" in p:
            for k,v in p["angle"].items():
                text += f"{pre}/ang/{k} {tup2str(v)}\n"
        if "theta" in p:
                min_, max_, unit_ = p['theta']
                text += f"{pre}/ang/mintheta {min_} {unit_}\n"
                text += f"{pre}/ang/maxtheta {max_} {unit_}\n"
        if "phi" in p:
                min_, max_, unit_ = p['phi']
                text += f"{pre}/ang/minphi {min_} {unit_}\n"
                text += f"{pre}/ang/maxphi {max_} {unit_}\n"
        if "position" in p:
            for k,v in p["position"].items():
                text += f"{pre}/pos/{k} {tup2str(v)}\n"
        if "confine" in p:
            text += f"{pre}/pos/confine {p['confine']}\n"
        return text


class SinglesDigi(Digi):
    def __init__(self, source, name, props):
        self.source = source
        self.name = name
        self.props = props
    def print(self):
        pre = f"/gate/digitizerMgr/{self.source}/SinglesDigitizer/Singles"
        text = f"{pre}/insert {self.name}\n"
        for k,v in self.props.items():
            text += f"{pre}/{self.name}/{k} {tup2str(v)}\n"
        return text

class Scanner(System):
    def __init__(self, parent, levels, sensitiveDetector):
        self.parent = parent
        self.levels = levels
        if isinstance(levels[0], list):
            self.l0 = levels[0][0].name
        else:
            self.l0 = levels[0].name
        self.sd = sensitiveDetector
    def print_geo(self, parent, level, p, attach):
        if p.parent is not None:
            pre = f"/gate/{p.parent}/daughters"
        else:
            pre = f"/gate/{parent}/daughters"
        text = f"{pre}/name {p.name}\n"
        if level == 1:
            text += f"{pre}/systemType scanner\n"
        text += f"{pre}/insert {p.geo}\n"
        text += p.print()
        if attach == True:
            text += f"/gate/systems/{self.l0}/level{level}/attach {p.name}\n"
        return text
    def print(self):
        text = f"##### -- SCANNER -- #####\n"
        parent = self.parent
        for i,l in enumerate(self.levels):
            level = i + 1
            text += f"# -- Level {level} -- #\n"
            if isinstance(l, list):
                for l2 in l:
                    if l2 == l[0]:
                        attach=True
                    else:
                        attach=False
                    text += self.print_geo(parent, level, l2, attach=attach)
                parent = l[0].name
            else:
                text += self.print_geo(parent, level, l, attach=True)
                parent = l.name
        text += f"# -- Sensitive detector -- #\n"
        text += f"/gate/{self.sd}/attachCrystalSD\n"
        return text

class Box(Primitive):
    def __init__(self, name, size, material, position, parent=None,
                 rotations=None, color=None, repeaters=None, motion=None):
        super().__init__(name, parent, "box", material, position, rotations,
                         color, repeaters, motion)
        self.size = size
    def print(self):
        text = super().print()
        s = self.size
        pre = f"/gate/{self.name}/geometry"
        text += f"{pre}/setXLength {s[0]} {s[3]}\n"
        text += f"{pre}/setYLength {s[1]} {s[3]}\n"
        text += f"{pre}/setZLength {s[2]} {s[3]}\n"
        return text
    def dict(self):
        props = super().dict() | {"size": self.size}
        return {"box": props}

class Cylinder(Primitive):
    def __init__(self, name, radius, height, material, position,
                 parent=None, rotations=None, phi=None, color=None,
                 repeaters=None, motion=None):
        super().__init__(name, parent, "cylinder", material, position,
                         rotations, color, repeaters, motion)
        self.radius = radius
        self.height = height
        self.phi = phi
    def print(self):
        text = super().print()
        r = self.radius
        h = self.height
        p = self.phi
        pre = f"/gate/{self.name}/geometry"
        text += f"{pre}/setRmin {r[0]} {r[2]}\n"
        text += f"{pre}/setRmax {r[1]} {r[2]}\n"
        text += f"{pre}/setHeight {h[0]} {h[1]}\n"
        if p is not None:
            text += f"{pre}/setPhiStart {p[0]} {p[2]}\n"
            text += f"{pre}/setDeltaPhi {p[1]} {p[2]}\n"
        return text

class RootOutput(Output):
    def __init__(self, filename, flags):
        self.filename = filename
        self.flags = flags
    def print(self):
        pre = "/gate/output/root"
        text = f"{pre}/enable\n"
        text += f"{pre}/setFileName {self.filename}\n"
        if "Hits" not in self.flags:
            text += f"{pre}/setRootHitFlag 0\n"
        if "Singles" not in self.flags:
            text += f"{pre}/setRootSinglesFlag 0\n"
        for f in self.flags:
            text += f"{pre}/setRoot{f}Flag 1\n"
        return text

class TreeOutput(Output):
    def __init__(self, filenames, hits, collections=None):
        self.filenames = filenames
        self.hits = hits
        self.collections = collections
    def print(self):
        pre = "/gate/output/tree"
        text = f"{pre}/enable\n"
        if isinstance(self.filenames, list):
            for f in self.filenames:
                text += f"{pre}/addFileName {f}\n"
        else:
            text += f"{pre}/addFileName {self.filenames}\n"
        if self.hits is not None:
            text += f"{pre}/hits/enable\n"
        if self.collections is not None:
            for c in self.collections:
                text += f"{pre}/addCollection {c}\n"
        return text

# main application class

class Application:
    def __init__(self):
        self.sources = []
        self.systems = []
        self.outputs = []
        self.digis = []
        self.actors = []
        self.primitives = []
        self.attribs = []
        self.world = {"x": 1, "y": 1, "z": 1, "unit": "m", "material": "Vacuum"}
        self.matpath = "GateMaterials.db"
        self.physics = "emstandard_opt4"
        self.slice_duration = 1
        self.time_stop = 1
        self.time_start = 0
        self.vis = None

    def set(self, text):
        self.attribs.append(text)

    def setTimeStop(self, t):
        self.time_stop = t

    def setTimeStart(self, t):
        self.time_start = t

    def setTimeSliceDuration(self, t):
        self.slice_duration = t

    def setMatpath(self, path):
        self.matpath = path

    def setPhysics(self, physics):
        self.physics = physics

    def setWorld(self, x, y, z, unit, material=None):
        self.world["x"] = x
        self.world["y"] = y
        self.world["z"] = z
        self.world["unit"] = unit
        self.world["material"] = material

    def setVis(self, props):
        self.vis = props

    def add(self, something):
        if isinstance(something, Output):
            self.outputs.append(something)
        if isinstance(something, System):
            self.systems.append(something)
        if isinstance(something, Digi):
            self.digis.append(something)
        if isinstance(something, Source):
            self.sources.append(something)
        if isinstance(something, Actor):
            self.actors.append(something)
        if isinstance(something, Primitive):
            self.primitives.append(something)

    def print(self):
        text = ""
        if self.vis is not None:
            text += "# NOTE: Visualisation enabled: Setting all activities to 1e3 Bq\n"
            for s in self.sources:
                if "activity" in s.props:
                    s.props["activity"] = (1e3, "becquerel")
        text += self.print_mat()
        text += self.print_phys()
        text += self.print_world()
        text += self.print_primitives()
        text += self.print_systems()
        text += self.print_actors()
        text += self.print_digis()
        text += self.print_attribs()
        text += self.print_init()
        text += self.print_sources()
        text += self.print_outputs()
        text += self.print_vis()
        text += self.print_start()
        return text

    def print_actors(self):
        text = "\n# Actors\n\n"
        for a in self.actors:
            text += a.print()
        return text

    def print_vis(self):
        text = "\n# Visualization\n\n"
        if self.vis is None:
            return ""
        text += f"/vis/open OGLSQt\n"
        text += f"/vis/viewer/reset\n"
        text += f"/vis/drawVolume\n"
        text += f"/vis/scene/add/hits\n"
        text += f"/tracking/storeTrajectory 1\n"
        text += f"/vis/scene/add/trajectories\n"
        # text += f"/gate/application/setTotalNumberOfPrimaries 100\n"
        for k,v in self.vis.items():
            if k in ["style", "viewpointThetaPhi"]:
                pre = "/vis/viewer/set"
            elif k in ["zoom"]:
                pre = "/vis/viewer"
            elif k in ["endOfEventAction"]:
                pre = "/vis/scene"
            elif k in ["auxiliaryEdges"]:
                if v is True:
                    text += f"/vis/viewer/set/auxiliaryEdge true\n"
                continue
            elif k in ["axes"]:
                if v is True:
                    text += f"/vis/scene/add/axes\n"
                continue
            else:
                pre = "/vis"
            text += f"{pre}/{k} {tup2str(v)}\n"
        return text

    def print_mat(self):
        mat = f"{self.matpath}"
        text = f"/gate/geometry/setMaterialDatabase {mat}\n"
        return text

    def print_phys(self):
        text = "\n# Physics\n\n"
        text += f"/gate/physics/addPhysicsList {self.physics}\n"
        return text

    def print_world(self):
        text = "\n# World\n\n"
        u = self.world["unit"]
        text += f"/gate/world/geometry/setXLength {self.world['x']} {u}\n"
        text += f"/gate/world/geometry/setYLength {self.world['y']} {u}\n"
        text += f"/gate/world/geometry/setZLength {self.world['z']} {u}\n"
        if self.world['material'] is not None:
            text += f"/gate/world/setMaterial {self.world['material']}\n"
        text += f"/gate/world/vis/forceWireframe true\n"
        return text

    def print_outputs(self):
        text = "\n# Outputs\n\n"
        for o in self.outputs:
            text += o.print()
        return text

    def print_primitives(self):
        text = "\n# Primitives\n\n"
        for p in self.primitives:
            pre = f"/gate/world/daughters"
            text += f"{pre}/name {p.name}\n"
            text += f"{pre}/insert {p.geo}\n"
            text += p.print()
        return text

    def print_systems(self):
        text = "\n# Systems\n\n"
        for s in self.systems:
            text += s.print()
        return text

    def print_digis(self):
        text = "\n# Digitizers\n\n"
        for d in self.digis:
            text += d.print()
        return text

    def print_sources(self):
        text = "\n# Sources\n\n"
        for s in self.sources:
            text += s.print()
        return text

    def print_attribs(self):
        text = "\n# Attributes\n\n"
        for a in self.attribs:
            text += a + "\n"
        return text

    def print_init(self):
        text = "\n# Init\n\n"
        text += "/gate/run/initialize\n"
        text += "/run/printProgress 100000\n"
        return text

    def print_start(self):
        text = "\n# Start\n\n"
        text += "/gate/random/setEngineName MersenneTwister\n"
        text += "/gate/random/setEngineSeed auto\n"
        text += f"/gate/application/setTimeSlice {self.slice_duration} s\n"
        text += f"/gate/application/setTimeStart {self.time_start} s\n"
        text += f"/gate/application/setTimeStop {self.time_stop} s\n"
        text += "/gate/application/startDAQ\n"
        return text

# utilities

def tup2str(tup):
    if isinstance(tup, tuple):
        return " ".join(map(str,(tup)))
    else:
        return str(tup)

