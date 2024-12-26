from nicegui import app, ui
from gate_macro_gen import *
import asyncio
import time
import shutil
import json
import uproot
import math
import numpy as np
from matplotlib import pyplot as plt

app.add_static_files('/assets', 'assets')

class App:
	def __init__(self):
		self.e_mev = 1
		self.thickness = 1
		self.activity = 30000
		self.tmpfile_vis = "/tmp/xsim_vis.mac"
		self.tmpfile = "/tmp/xsim.mac"
		self.status = "Stopped"
		self.log = None
		self.entries = {}
		self.logscale = {
				"singles": False,
				"incoming": False,
				"outgoing": False
		}
		self.plot_in = None
		self.plot_out = None

	def generate_script(self, vis=False):
		# Simulation is done in vacuum, not in air
		a = Application()
		a.setWorld(0.2, 0.2, 0.5, "m")
		a.add(SourceGps("gammas", particle="gamma", mono=(self.e_mev, "MeV"),
				  activity=(self.activity, "becquerel"),
				  angle={"type": "iso"}, position={"centre": (0,0,25,"cm")}))
		zpos = -5
		# This is the material to be simulated
		c = Box(name="crystal", size=(10,10,self.thickness,"cm"),
		  position=(0,0,zpos,"cm"), material="CsITl")
		a.add(Scanner("world", levels=[c],
				sensitiveDetector="crystal"))
		a.add(SimulationStatisticActor("stats", "stats.txt"))
		# These are used to record the spectrum before and after the material
		pa1 = Box(name="recorder1", size=(10,10,0.1,"cm"),
			position=(0,0,zpos+self.thickness/2+0.1/2,"cm"),
			material="Vacuum")
		pa2 = Box(name="recorder2", size=(10,10,0.1,"cm"),
			position=(0,0,zpos-self.thickness/2-0.1/2,"cm"),
			material="Vacuum")
		a.add(pa1)
		a.add(pa2)
		a.add(PhaseSpaceActor("phasespace1", "psa1.root", attach="recorder1"))
		a.add(PhaseSpaceActor("phasespace2", "psa2.root", attach="recorder2"))
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
		self.status = "Plotting..."
		self.plot_singles()
		self.plot_input_spectrum()
		self.plot_outgoing_spectrum()
		self.log_add_stats()

	def log_add_stats(self):
		c = self.log.content
		c += ("\n"
			+ f"# Incoming gammas: {self.entries["incoming"]}\n"
			+ f"# Outgoing gammas: {self.entries["outgoing"]}\n"
			+ f"# Detected gammas: {self.entries["singles"]}\n"
		)
		self.log.content = c

	def plot_singles(self):
		t = self.get_tree("tree.Singles.root", "tree")
		b = t.arrays()
		self.entries["singles"] = t.num_entries
		with self.plot as p:
			self.plot_histogram(p, b["energy"], self.logscale["singles"])

	def plot_input_spectrum(self):
		if self.plot_in is None:
			return
		t = self.get_tree("psa1.root", "PhaseSpace")
		b = t.arrays()
		self.entries["incoming"] = t.num_entries
		with self.plot_in as p:
			self.plot_histogram(p, b["Ekine"], self.logscale["incoming"])

	def plot_outgoing_spectrum(self):
		if self.plot_out is None:
			return
		t = self.get_tree("psa2.root", "PhaseSpace")
		b = t.arrays()
		self.entries["outgoing"] = t.num_entries
		with self.plot_out as p:
			self.plot_histogram(p, b["Ekine"], self.logscale["outgoing"])

	def get_tree(self, filename, treename):
		f = uproot.open(filename) # TreeOutput
		n_tries = 0
		while n_tries < 3:
			n_tries += 1
			try:
				t = f[treename]
				return t
			except Exception as e:
				print(e)
				print(f"No tree {treename} in {filename}. Trying again.")
				time.sleep(2)
				raise e
		if n_tries == 3:
			self.status = f"No {treename} data. Cannot plot."
			return None

	def plot_histogram(self, p, arr, log):
		p.clear()
		plt.clf()
		keV_per_bin = 10
		n_bins = math.ceil(self.e_mev * 1.1 / keV_per_bin * 1000)
		n_bins = 100
		bins = np.linspace(0, self.e_mev * 1.1, n_bins)
		if log:
			plt.yscale("log")
		plt.hist(arr, bins)
		return plt.gca()


	async def simulate(self):
		await self.rebuild()
		# Run again for simulation
		self.status = "Simulation running..."
		script = self.generate_script()
		self.write_script(script, self.tmpfile)
		await self.run_script(self.tmpfile)
		with open("stats.txt", "r") as f:
			self.log.content = "".join(f.readlines())
		self.display()
		self.status = "Simulation done."

	def toggle_log(self, which):
		self.logscale[which] = not self.logscale[which]
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
		with ui.row():
			ui.button("Rebuild!", on_click=a.rebuild)
			ui.button("Simulate!", on_click=a.simulate)
			ui.button("Plot!", on_click=lambda: a.display())
		l = ui.label("Simulation stopped")
		l.bind_text(target_object=a, target_name="status")
	dist = 300
	with ui.row():
		with ui.column():
			ui.label("3D view")
			with ui.scene(grid=False,width=300,height=300) as scene:
				a.gltf = scene.gltf(f'assets/scene_trajectories.gltf?{time.time()}')
				scene.move_camera(x=dist*0.6,y=dist*0.4,z=20)
		with ui.column():
			ui.label("Front view")
			with ui.scene_view(scene,width=300,height=300,
					  camera=ui.scene.orthographic_camera(size=500)) as view1:
				view1.move_camera(x=dist,y=0,z=0)
		with ui.column():
			ui.label("Side view")
			with ui.scene_view(scene,width=300,height=300,
					  camera=ui.scene.orthographic_camera(size=500)) as view1:
				view1.move_camera(x=0,y=dist,z=0)
	a.log = ui.code()
	with ui.column():
		ui.label("Detected spectrum")
		a.plot = ui.pyplot(close=False, figsize=(10,4))
		with ui.row():
			ui.button("Lin/log", on_click=lambda: a.toggle_log("singles"))
	with ui.column():
		ui.label("Incoming spectrum")
		a.plot_in = ui.pyplot(close=False, figsize=(10,4))
		with ui.row():
			ui.button("Lin/log", on_click=lambda: a.toggle_log("incoming"))
	with ui.column():
		ui.label("Outgoing spectrum")
		a.plot_out = ui.pyplot(close=False, figsize=(10,4))
		with ui.row():
			ui.button("Lin/log", on_click=lambda: a.toggle_log("outgoing"))

ui.run()
