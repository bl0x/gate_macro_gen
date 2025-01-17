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
		self.activity = 30000
		self.tmpfile_vis = "/tmp/xsim_vis.mac"
		self.tmpfile = "/tmp/xsim.mac"
		self.status = "Stopped"
		self.log = None
		self.logscale = {
				"singles": False,
				"incoming": False,
				"outgoing": False
		}
		self.plot_in = None
		self.plot_out = None
		self.blocks = []
		self.block_list = None
		self.materials = []
		self.load_materials("GateMaterials.db")

	def load_materials(self, filename):
		with open(filename) as f:
			content = f.readlines()
			section = None
			for l in content:
				line = l.strip()
				if line == "[Materials]":
					section = "Materials"
				if section == "Materials" and len(line) > 0 and line[0].isalpha():
					parts = line.split(":", 1)
					name = parts[0]
					self.materials.append(name)
		self.materials.sort()
		print(self.materials)

	class Block():
		def __init__(self, name):
			self.thickness = 1
			self.width = 10
			self.length = 10
			self.distance = 10
			self.material = "CsITl"
			self.entries = {}
			with a.block_list:
				with ui.card() as self.card:
					with ui.row():
						ui.label("Absorber")
						ui.button("Remove", on_click=lambda: a.remove_block(self))
					with ui.card_section():
						with ui.grid(columns=2):
							ui.number(label="Length [mm]:",
				  		    	value=self.length,
			        			format="%.3f",
			        			on_change=lambda e: self.set_length(e.value))
							ui.number(label="Width [mm]:",
				  		    	value=self.width,
			        			format="%.3f",
			        			on_change=lambda e: self.set_width(e.value))
							ui.number(label="Thickness [mm]:",
				  		    	value=self.thickness,
			        			format="%.3f",
			        			on_change=lambda e: self.set_thickness(e.value))
							ui.number(label="Distance [mm]:",
								value=self.distance,
			        			format="%.3f",
			        			on_change=lambda e: self.set_distance(e.value))
							ui.select(label="Material", options=a.materials,
								with_input=True,
								on_change=lambda e: self.set_material(e.value))
		def set_width(self, t):
			self.width = t
		def set_length(self, t):
			self.length = t
		def set_thickness(self, t):
			self.thickness = t
		def set_distance(self, t):
			self.distance = t
		def set_material(self, t):
			self.material = t

	def add_block(self, name):
		self.blocks.append(self.Block(name))

	def remove_block(self, block):
		self.block_list.remove(block.card)
		if block in self.blocks:
			self.blocks.remove(block)

	def add_initial_blocks(self):
		with a.block_list:
			with ui.card():
				ui.label("Generator")
				with ui.card_section():
					with ui.row(wrap=False):
						ui.number(label="Energy [MeV]:", value=a.e_mev,
			       	   	   format="%.3f",
		   	   	   	   	   on_change=lambda e: a.set_energy(e.value))
						ui.number(label="Activity [Bq]:", value=a.activity,
			       	   	   format="%d",
		   	   	   	   	   on_change=lambda e: a.set_activity(e.value))
		self.add_block("Absorber")

	def generate_script(self, vis=False):
		# Simulation is done in vacuum, not in air
		a = Application()
		a.setWorld(0.2, 0.2, 0.5, "m")
		a.add(SourceGps("gammas", particle="gamma", mono=(self.e_mev, "MeV"),
				  activity=(self.activity, "becquerel"),
				  angle={"type": "iso"}, position={"centre": (0,0,25,"cm")}))
		zpos = 250
		a.add(SimulationStatisticActor("stats", "stats.txt"))
		# This is the material to be simulated
		blocks = []
		for i,b in enumerate(self.blocks):
			zpos -= b.distance
			name = f"block_{i}"
			syst = f"system_{i}"
			psa1 = f"psa1_{i}.root"
			psa2 = f"psa2_{i}.root"
			c = Box(name=name, size=(b.length,b.width,b.thickness,"mm"),
		  	  position=(0,0,zpos,"mm"), material=b.material)
			a.add(Scanner("world", levels=[c],
					sensitiveDetector=name))
			a.add(PhaseSpaceActor(f"phasespace_in_{i}", psa1,
						 attach=name))
			a.add(PhaseSpaceActor(f"phasespace_out_{i}", psa2,
						 attach=name, outgoing=True))
			if not vis:
				a.add(SinglesDigi(name, "adder",
                 	 	 	 	 {"positionPolicy": "energyWeightedCentroid"}))
				a.add(SinglesDigi(name, "readout", {"setDepth": 1}))
				a.add(SinglesDigi(name, "energyResolution",
                 	 	 	 	 {"fwhm": 0.002, "energyOfReference": (662, "keV")}))
				a.add(SinglesDigi(name, "pileup",
                 	 	 	 	 {"setPileupVolume": name, "setPileup": (4, "ns")}))
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
		try:
			self.gltf = scene.gltf(
					f'assets/scene_trajectories.gltf?{time.time()}')
		except:
			pass

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
		for i,b in enumerate(self.blocks):
			c = ("\n"
				+ f"# Incoming block {i}: {b.entries["incoming"]}\n"
				+ f"# Outgoing block {i}: {b.entries["outgoing"]}\n"
				+ f"# Detected block {i}: {b.entries["singles"]}\n"
			)
			self.log.push(c)

	def plot_singles(self):
		for i,bl in enumerate(self.blocks):
			if len(self.blocks) == 1:
				rootfilename = "tree.Singles.root"
			else:
				rootfilename = f"tree.Singles_block_{i}.root"
			t = self.get_tree(rootfilename, "tree")
			b = t.arrays()
			bl.entries["singles"] = t.num_entries
			with self.plot as p:
				self.plot_histogram(p, b["energy"], self.logscale["singles"])

	def plot_input_spectrum(self):
		for i,bl in enumerate(self.blocks):
			if self.plot_in is None:
				return
			t = self.get_tree(f"psa1_{i}.root", "PhaseSpace")
			b = t.arrays()
			bl.entries["incoming"] = t.num_entries
			with self.plot_in as p:
				self.plot_histogram(p, b["Ekine"], self.logscale["incoming"])

	def plot_outgoing_spectrum(self):
		for i,bl in enumerate(self.blocks):
			if self.plot_out is None:
				return
			t = self.get_tree(f"psa2_{i}.root", "PhaseSpace")
			b = t.arrays()
			bl.entries["outgoing"] = t.num_entries
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
			text = "".join(f.readlines())
			self.log.push(text)
		self.display()
		self.status = "Simulation done."

	def toggle_log(self, which):
		self.logscale[which] = not self.logscale[which]
		self.display()

	def set_energy(self, e):
		self.e_mev = e
	def set_activity(self, a):
		self.activity = a

a = App()

with ui.row(wrap=False):
	with ui.column().classes('w-1/2'):
		a.block_list = ui.scroll_area().classes('w-full h-96 border')
		a.add_initial_blocks()
		with ui.row():
			ui.button("Add", on_click=lambda: a.add_block("Absorber"))
			ui.button("Rebuild!", on_click=a.rebuild)
			ui.button("Simulate!", on_click=a.simulate)
			ui.button("Plot!", on_click=lambda: a.display())

		l = ui.label("Simulation stopped")
		l.bind_text(target_object=a, target_name="status")
		a.log = ui.log().classes('h-128')

	dist = 300
	with ui.column().classes('w-full'):
		with ui.row(wrap=False):
			with ui.column():
				ui.label("3D view")
				with ui.scene(grid=False,width=300,height=300) as scene:
					asset = f'assets/scene_trajectories.gltf?{time.time()}'
					a.gltf = scene.gltf(asset)
					scene.move_camera(x=dist*0.6,y=dist*0.4,z=20)
			with ui.column():
				ui.label("Front view")
				with ui.scene_view(scene,width=300,height=300,
					  	  camera=ui.scene.orthographic_camera(size=50)) as view1:
					view1.move_camera(x=dist,y=0,z=0)
			with ui.column():
				ui.label("Side view")
				with ui.scene_view(scene,width=300,height=300,
					  	  camera=ui.scene.orthographic_camera(size=50)) as view1:
					view1.move_camera(x=0,y=dist,z=0)
		with ui.column():
			ui.label("Detected spectrum")
			a.plot = ui.pyplot(close=False, figsize=(10,4))
			with ui.row():
				ui.button("Lin/log",
			    on_click=lambda: a.toggle_log("singles"))
		with ui.column():
			ui.label("Incoming spectrum")
			a.plot_in = ui.pyplot(close=False, figsize=(10,4))
			with ui.row():
				ui.button("Lin/log",
			    on_click=lambda: a.toggle_log("incoming"))
		with ui.column():
			ui.label("Outgoing spectrum")
			a.plot_out = ui.pyplot(close=False, figsize=(10,4))
			with ui.row():
				ui.button("Lin/log",
			    on_click=lambda: a.toggle_log("outgoing"))

ui.run()
