class Application:
    def __init__(self):
        self.sources = []
        self.daughters = []
        self.outputs = []
        self.digis = []
        self.world = {"x": 0, "y": 0, "z": 0, "unit": None}
        self.matpath = "/home/bloeher/opt/Gate-9.3"
        self.physics = "emstandard"
        self.vis = None

    def setWorld(self, x, y, z, unit):
        self.world["x"] = x
        self.world["y"] = y
        self.world["z"] = z
        self.world["unit"] = unit

    def setVis(self, props):
        self.vis = props

    def addRootOutput(self, filename, flags):
        o = {}
        o["name"] = "root"
        o["filename"] = filename
        o["flags"] = flags
        self.outputs.append(o)

    def addTreeOutput(self, filenames, hits, collections):
        o = {}
        o["name"] = "tree"
        o["filenames"] = filenames
        o["hits"] = hits
        o["collections"] = collections
        self.outputs.append(o)

    def addSourceGps(self, name, **kwargs):
        s = {}
        s["name"] = name
        s["gps"] = True
        for k,v in kwargs.items():
            s[k] = v
        self.sources.append(s)

    def addSinglesDigi(self, source, name, props = None):
        d = {}
        d["type"] = "singles"
        d["source"] = source
        d["name"] = name
        d["props"] = props
        self.digis.append(d)

    def addDaughter(self, parent, name, systemType, props):
        d = {}
        d["parent"] = parent
        d["name"] = name
        d["props"] = props
        d["type"] = systemType
        self.daughters.append(d)

    def start(self):
        self.print_mat()
        self.print_phys()
        self.print_world()
        self.print_daughters()
        self.print_digis()
        self.print_init()
        self.print_sources()
        self.print_outputs()
        self.print_vis()
        self.print_start()

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
            print(f"{pre}/{k} {self.tup2str(v)}")


    def print_mat(self):
        mat = f"{self.matpath}/GateMaterials.db"
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

    def tup2str(self, tup):
        if isinstance(tup, tuple):
            return " ".join(map(str,(tup)))
        else:
            return str(tup)

    def print_output_root(self, o):
        print("\n# Output root\n")
        pre = "/gate/output/root"
        print(f"{pre}/enable")
        print(f"{pre}/setFileName {o['filename']}")
        for f in o["flags"]:
            print(f"{pre}/setRoot{f}Flag 1")

    def print_output_tree(self, o):
        print("\n# Output tree\n")
        pre = "/gate/output/tree"
        print(f"{pre}/enable")
        for f in o['filenames']:
            print(f"{pre}/addFileName {f}")
        if o['hits']:
            print(f"{pre}/hits/enable")
        for c in o['collections']:
            print(f"{pre}/addCollection {c}")


    def print_outputs(self):
        for o in self.outputs:
            if o["name"] == "tree":
                self.print_output_tree(o)
            elif o["name"] == "root":
                self.print_output_root(o)

    def print_daughters(self):
        print("\n# Volumes\n")
        for d in self.daughters:
            parent = d['parent']
            name = d['name']
            pre = f"/gate/{parent}/daughters"
            p = d['props']
            print(f"{pre}/name {name}")
            print(f"{pre}/systemType {d['type']}")
            print(f"{pre}/insert {p['primitive']}")
            pre = f"/gate/{name}"
            if "material" in p:
                print(f"{pre}/setMaterial {p['material']}")
            if "position" in p:
                print(f"{pre}/placement/setTranslation {self.tup2str(p['position'])}")
            if "size" in p:
                s = p['size']
                pre = f"/gate/{name}/geometry"
                print(f"{pre}/setXLength {s[0]} {s[3]}")
                print(f"{pre}/setYLength {s[1]} {s[3]}")
                print(f"{pre}/setZLength {s[2]} {s[3]}")
            if "attach" in p:
                print(f"/gate/systems/{name}/level{p['attach']}/attach {name}")
                print(f"/gate/{name}/attachCrystalSD")

    def print_digis_singles(self, d):
        src = d["source"]
        pre = f"/gate/digitizerMgr/{src}/SinglesDigitizer/Singles"
        print(f"{pre}/insert {d['name']}")
        for k,v in d["props"].items():
            print(f"{pre}/{d['name']}/{k} {self.tup2str(v)}")


    def print_digis(self):
        print("\n# Digitizers\n")
        for d in self.digis:
            if d["type"] == "singles":
                self.print_digis_singles(d)

    def print_sources(self):
        print("\n# Sources\n")
        for s in self.sources:
            name = s['name']
            pre = f"/gate/source/{name}"
            if "gps" in s:
                print(f"/gate/source/addSource {name} gps")
            else:
                print(f"/gate/source/addSource {name}")
            if "activity" in s:
                print(f"{pre}/setActivity {self.tup2str(s['activity'])}")
            pre += "/gps"
            if "particle" in s:
                print(f"{pre}/particle {s['particle']}")
            if "mono" in s:
                print(f"{pre}/ene/mono {self.tup2str(s['mono'])}")
            if "angle" in s:
                for k,v in s["angle"].items():
                    print(f"{pre}/ang/{k} {self.tup2str(v)}")
            if "position" in s:
                for k,v in s["position"].items():
                    print(f"{pre}/pos/{k} {self.tup2str(v)}")

    def print_init(self):
        print("\n# Init\n")
        print("/gate/run/initialize")

    def print_start(self):
        print("\n# Start\n")
        print("/gate/random/setEngineName MersenneTwister")
        print("/gate/random/setEngineSeed auto")
        print("/gate/application/startDAQ")

