# Made by Fab4key
# Version 1.0

class CgmScene():
	def __init__(self, scene_name:str, size_x:int, size_y:int, render_bg:str):
		self.name = scene_name
		self.objects = []
		self.size_x = size_x
		self.size_y = size_y
		self.render_bg = render_bg
		
class CgmObject():
	def __init__(self, name:str, symbol:str, x:int, y:int, layer:int):
		self.name = name
		self.symbol = symbol
		self.x = x
		self.y = y
		self.layer = layer

class CgmPixel():
	def __init__(self, x:int, y:int, pool):
		self.x = x
		self.y = y
		self.pool = pool

class Cgm():
	def __init__(self):
		self.version == "1.0"
		self.scenes = []
		self.active_scene = None
		
	def version(self):
		return self.version
	
	def clear_screen(self):
		import os
		os.system("cls|clear")
	
	def create_scene(self, scene_name:str, size_x:int, size_y:int, render_bg:str=None):
		if render_bg == None:
			render_bg = ""
			
		scene_maked = 0
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					scene_maked = 1
					return None
		
		self.scenes.append(CgmScene(scene_name, size_x, size_y, render_bg))
	
	def get_scenes(self):
		return self.scenes
	
	def get_scene(self, scene_name:str):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					return self.scenes[scene_i]
	
	def get_scene_objects(self, scene_name:str):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					return self.scenes[scene_i].objects
	
	def get_scene_object(self, scene_name:str, object_name:str):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					if len(self.scenes[scene_i].objects) != 0:
						for object_i in range(len(self.scenes[scene_i].objects)):
							if object_name == self.scenes[scene_i].objects[object_i].name:
								return self.scenes[scene_i].objects[object_i]
	
	def set_scene_options(self, scene_name:str, new_name:str=None, new_size_x:int=None, new_size_y:int=None, new_render_bg:str=None):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					if new_name != None:
						self.scenes[scene_i].name = new_name
					if new_size_x != None:
						self.scenes[scene_i].size_x = new_size_x
					if new_size_y != None:
						self.scenes[scene_i].size_y = new_size_y
					if new_render_bg != None:
						self.scenes[scene_i].render_bg = new_render_bg
					
					return None
	
	def set_object_options(self, scene_name:str, object_name:str, new_name:str=None, new_x:int=None, new_y:int=None, new_symbol:str=None, new_layer:int=None):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					if len(self.scenes[scene_i].objects) != 0:
						for object_i in range(len(self.scenes[scene_i].objects)):
							if object_name == self.scenes[scene_i].objects[object_i].name:
								if new_name != None:
									self.scenes[scene_i].objects[object_i].name = new_name
								if new_x != None:
									self.scenes[scene_i].objects[object_i].x = new_x
								if new_y != None:
									self.scenes[scene_i].objects[object_i].y = new_y
								if new_symbol != None:
									self.scenes[scene_i].objects[object_i].symbol = new_symbol
								if new_layer != None:
									self.scenes[scene_i].objects[object_i].layer = new_layer
								
								return None
	
	def delete_scene(self, scene_name:str):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					self.scenes.remove(self.scenes[scene_i])
					return None
	
	def create_object(self, scene_name:str, name:str, symbol:str, x:int, y:int, layer:int):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					self.scenes[scene_i].objects.append(CgmObject(name, symbol, x, y, layer))
					return None
	
	def delete_object(self, scene_name:str, object_name:str):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					if len(self.scenes[scene_i].objects) != 0:
						for object_i in range(len(self.scenes[scene_i].objects)):
							if object_name == self.scenes[scene_i].objects[object_i].name:
								self.scenes[scene_i].objects.remove(self.scenes[scene_i].objects[object_i])
								return None
	
	def set_active_scene(self, scene_name:str):
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
					self.active_scene = self.scenes[scene_i].name
					return None
	
	def render_scene(self, scene_name):
		import time
		if len(self.scenes) != 0:
			for scene_i in range(len(self.scenes)):
				if scene_name == self.scenes[scene_i].name:
				
					pool = []
				
					for y in range(self.scenes[scene_i].size_y):
						linepool = []
						for x in range(self.scenes[scene_i].size_x):
							linepool.append(CgmPixel(x, y, CgmObject("BG", self.scenes[scene_i].render_bg, x, y, 0)))
						pool.append(linepool)
							
					for y in range(self.scenes[scene_i].size_y):
						for x in range(self.scenes[scene_i].size_x):
							for object_i in range(len(self.scenes[scene_i].objects)):
								if x == round(self.scenes[scene_i].objects[object_i].x):
									if y == round(self.scenes[scene_i].objects[object_i].y):
										try:
											if pool[x][y].pool == self.scenes[scene_i].render_bg:
												pool[x][y].pool = self.scenes[scene_i].objects[object_i]
											else:
												if pool[x][y].pool.layer < self.scenes[scene_i].objects[object_i].layer:
													pool[x][y] = self.scenes[scene_i].objects[object_i]
										except AttributeError:
											if pool[x][y] == self.scenes[scene_i].render_bg:
												pool[x][y] = self.scenes[scene_i].objects[object_i]
											else:
												if pool[x][y].layer < self.scenes[scene_i].objects[object_i].layer:
													pool[x][y] = self.scenes[scene_i].objects[object_i]
					
					for y in range(self.scenes[scene_i].size_y):
						for x in range(self.scenes[scene_i].size_x):
							try:
								print(pool[x][y].symbol, end=" ")
							except AttributeError:
								print(pool[x][y].pool.symbol, end=" ")
						print()
		time.sleep(0.017)
	
	def render(self):
		if len(self.scenes) != 0:
			if self.active_scene != None:
				for scene_i in range(len(self.scenes)):
					if self.active_scene == self.scenes[scene_i].name:
						self.render_scene(self.active_scene)
						return None
				print("SELECTED SCENE NOT FOUND")
			else:
				print("SCENE NOT SELECTED")
		else:
			print("SCENES NOT FOUND")
