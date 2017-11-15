import pygame as pg 
from pytmx.util_pygame import load_pygame
from settings import *
import pytmx

class Map:
	def __init__(self,filename):
		self.data = []
		with open(filename,'rt') as f:
			for line in f:
				self.data.append(line)
		self.tilewidth = len(self.data[0])
		self.tileheight = len(self.data)
		self.width = self.tilewidth * TILESIZE
		self.height = self.tilewidth * TILESIZE

class TiledMap:
	def __init__(self,filename):
		tm = load_pygame(filename, pixelalpha=True)
		self.width = tm.width*tm.tilewidth
		self.height = tm.height*tm.tileheight
		self.tmxdata = tm

	def render(self, surface):
		ti = self.tmxdata.get_tile_image_by_gid
		for layer in self.tmxdata.visible_layers:
			if isinstance(layer, pytmx.TiledTileLayer):
				for x,y,gid in layer:
					tile = ti(gid)
					if tile:
						surface.blit(tile,(x*self.tmxdata.tilewidth,y*self.tmxdata.tileheight))

	def make_map(self):
		temp_surface = pg.Surface((self.width,self.height))
		self.render(temp_surface)
		return temp_surface


def collide_hit_rect(one, two):
	return one.hit_rect.colliderect(two)