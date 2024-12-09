from nicegui import app, ui
from gate_macro_gen import *
import asyncio
import time
import shutil
import json
import uproot
from matplotlib import pyplot as plt

app.add_static_files('/assets', 'assets')

class App:
	def __init__(self):
		self.e_mev = 1
		self.thickness = 10
		self.activity = 300000
		self.tmpfile_vis = "/tmp/xsim_vis.mac"
		self.tmpfile = "/tmp/xsim.mac"
		self.status = "Stopped"
		self.log = None

	def generate_script(self, vis=False):
		a = Application()
		# a.setWorld(10, 10, 10, "m")
		a.add(SourceGps("gammas", particle="gamma", mono=(self.e_mev, "MeV"),
				  activity=(self.activity, "becquerel"),
				  angle={"type": "iso"}, position={"centre": (0,0,25,"cm")}))
		c = Box(name="crystal", size=(10,10,self.thickness,"cm"),
		  position=(0,0,-5,"cm"), material="CsITl")
		a.add(Scanner("world", levels=[c], sensitiveDetector="crystal"))
		a.add(SimulationStatisticActor("stats", "stats.txt"))
		if not vis:
			a.add(SinglesDigi("crystal", "adder",
                 	 	 	 {"positionPolicy": "energyWeightedCentroid"}))
			a.add(SinglesDigi("crystal", "readout", {"setDepth": 1}))
			a.add(SinglesDigi("crystal", "energyResolution",
                 	 	 	 {"fwhm": 0.002, "energyOfReference": (662, "keV")}))
			a.add(SinglesDigi("crystal", "pileup",
                 	 	 	 {"setPileupVolume": "crystal", "setPileup": (4, "ns")}))
			# a.add(RootOutput(
        	# 		filename = "output",
        	# 		flags = ["Hit", "Singles_crystal", "Ntuple"]
			# ))
			a.add(TreeOutput(
        			filenames = "tree.root",
        			hits = True,
        			collections = ["Singles"]
			))
		if vis:
			a.setVis({
				"zoom": 10,
				"style": "surface",
			 	"endOfEventAction": "accumulate",
			 	"axes": False
			 })
			a.vis_type = "VTK_OFFSCREEN"
		return a

	def write_script(self, script, file):
		with open(file, "w") as f:
			f.write(script.print())

	async def run_script(self, file):
		print("-- GATE STARTING --")
		p = await asyncio.subprocess.create_subprocess_exec("Gate", file)
		while True:
			try:
				await asyncio.wait_for(p.wait(), timeout=1)
				break
			except asyncio.TimeoutError:
				print("-- WAITING --")
		print("-- GATE FINISHED --")

	def update_scene(self):
		if self.gltf is None:
			return
		self.gltf.delete()
		self.gltf = scene.gltf(
				f'assets/scene_trajectories.gltf?{time.time()}')

	async def rebuild(self):
		self.status = "Updating geometry..."
		# Run once for visualisation only
		script = self.generate_script(vis=True)
		self.write_script(script, self.tmpfile_vis)
		await self.run_script(self.tmpfile_vis)
		# Modify object color
		with open("scene_trajectories.gltf", "r") as f:
			data = json.load(f)
			# set world volume to transparent (does not work)
			data["materials"][0]["pbrMetallicRoughness"]["baseColorFactor"] = [0,0,1,0]
			# remove world volume mesh from renderer node
			for n in data["nodes"]:
				if n["name"] == "Renderer Node":
					n["children"] = n["children"][1:]
		with open("scene_trajectories.gltf", "w") as f:
			json.dump(data, f)

		shutil.move("scene_trajectories.gltf", "assets/scene_trajectories.gltf")
		self.update_scene()
		self.status = "Done"

	def display(self):
		# f = uproot.open("output.root") # RootOutput
		f = uproot.open("tree.Singles.root") # TreeOutput
		try:
			print(f.keys())
			# t = f["Singles_crystal"]
			t = f["tree"]
			print(t)
			b = t.arrays()
			with self.plot:
				plt.hist(b["energy"])
		except:
			print("No singles")


	async def simulate(self):
		await self.rebuild()
		# Run again for simulation
		self.status = "Simulation running..."
		script = self.generate_script()
		self.write_script(script, self.tmpfile)
		await self.run_script(self.tmpfile)
		self.status = "Simulation done."
		with open("stats.txt", "r") as f:
			self.log.content = "".join(f.readlines())
		self.display()


	def set_energy(self, e):
		self.e_mev = e
	def set_thickness(self, t):
		self.thickness = t
	def set_activity(self, a):
		self.activity = a

a = App()

with ui.grid(columns='1fr 2fr').classes('w-full'):
	with ui.column().classes('w-100'):
		ui.number(label="Energy [MeV]:", value=a.e_mev, format="%.3f",
		   on_change=lambda e: a.set_energy(e.value))
		ui.number(label="Thickness [mm]:", value=a.thickness, format="%.3f",
		   on_change=lambda e: a.set_thickness(e.value))
		ui.number(label="Activity [Bq]:", value=a.activity, format="%d",
		   on_change=lambda e: a.set_activity(e.value))
		ui.number(label="Activity [Bq]:", value=a.activity, format="%d",
		   on_change=lambda e: a.set_activity(e.value))
		ui.number(label="Activity [Bq]:", value=a.activity, format="%d",
		   on_change=lambda e: a.set_activity(e.value))
		ui.number(label="Activity [Bq]:", value=a.activity, format="%d",
		   on_change=lambda e: a.set_activity(e.value))
		ui.number(label="Activity [Bq]:", value=a.activity, format="%d",
		   on_change=lambda e: a.set_activity(e.value))
		ui.number(label="Activity [Bq]:", value=a.activity, format="%d",
		   on_change=lambda e: a.set_activity(e.value))
		with ui.row():
			ui.button("Rebuild!", on_click=a.rebuild)
			ui.button("Simulate!", on_click=a.simulate)
		l = ui.label("Simulation stopped")
		l.bind_text(target_object=a, target_name="status")
	with ui.scene(grid=False,width=300,height=300) as scene:
		a.gltf = scene.gltf(f'assets/scene_trajectories.gltf?{time.time()}')
		scene.move_camera(x=300*0.6,y=300*0.4,z=20)
	a.log = ui.code()
	a.plot = ui.pyplot()

ui.run()
