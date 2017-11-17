#Anatomy park game

import pygame as pg
import random
from settings import *
from sprites import *
from tilemap import *
from os import path

#HUD Functions
def text_to_screen(screen, text, x, y, size = 50,color = (200, 000, 000), font_type = './fonts/aerial.ttf'):
    try:

        text = str(text)
        font = pg.font.Font(font_type, size)
        text = font.render(text, True, color)
        screen.blit(text, (x, y))

    except Exception, e:
        print 'Font Error, saw it coming'
        raise e

def draw_player_health(surf,x,y,pct):
	if pct < 0 :
		pct = 0
	BAR_LENGTH = 100
	BAR_HEIGHT = 20
	fill = pct * BAR_LENGTH
	outline_rect  = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
	fill_rect = pg.Rect(x, y, fill,BAR_HEIGHT)
	if(pct > 0.6):
		col = GREEN 
	elif (pct>0.3):
		col = YELLOW
	else:
		col = RED
	pg.draw.rect(surf,col,fill_rect)
	pg.draw.rect(surf,WHITE,outline_rect,2)



class Game:
	def __init__(self):
		#initialize game window
		pg.init()
		#pg.mixer.init()
		self.screen = pg.display.set_mode((WIDTH,HEIGHT))
		pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
		pg.key.set_repeat(100,100)
		self.running = True

	def new(self):
		#start a new game
		self.healthDone = False
		self.all_sprites = pg.sprite.Group()
		self.walls = pg.sprite.Group()
		self.bacteria = pg.sprite.Group()
		self.bullets = pg.sprite.Group()
		self.acid_puddles = pg.sprite.Group()
		self.bac_bullets = pg.sprite.Group()
		self.wbc_protect = pg.sprite.Group()
		self.wbc_bullets = pg.sprite.Group()
		self.gun_type = 0
		cover = 1 
		bacteria_type = 0
		self.load_data()
		self.health_upgrade = Health_upgrade(self,vec(0,0))
		for row,tiles in enumerate(self.map.data):
			for col, tile in enumerate(tiles):
				if tile == '1':
					Wall(self,col,row)
				if tile == 'P':
					self.player = Player(self,col,row)
				if tile == 'M':
					Bacteria(self,col,row,bacteria_type)
					bacteria_type = (bacteria_type+1)%2
				if tile == 'A':
					Acid_Puddle(self,col,row)
				if tile == 'W':
					WBC_protect(self,col,row,cover)
					cover+=1


		self.paused = False
		self.run()

	
	def load_data(self):
		game_folder = path.dirname(__file__)
		
		self.map = Map("map.txt")
		
		self.player_img = pg.image.load("./images/morty.png")
		self.player_img = pg.transform.scale(self.player_img,(TILESIZE,TILESIZE))
		self.wall_img = pg.image.load("./images/png/element_blue_square.png")
		self.wall_img = pg.transform.scale(self.wall_img,(TILESIZE,TILESIZE))
		self.bac_img = pg.image.load("./images/Bacteria_Cell.png")
		self.bac_img = pg.transform.scale(self.bac_img,(TILESIZE,TILESIZE))
		self.bullet_img = pg.image.load("./images/bullet1.png")
		self.bullet_img = pg.transform.scale(self.bullet_img,(TILESIZE/4,TILESIZE/4))
		self.puddle_img = pg.image.load("./images/acid_puddle.png")
		self.puddle_img = pg.transform.scale(self.puddle_img,(TILESIZE*2,TILESIZE*2))
		self.wbc_img = pg.image.load("./images/WBC.png")
		self.wbc_img = pg.transform.scale(self.wbc_img,(TILESIZE,TILESIZE))
		self.gun_flashes = []
		for img in MUZZLE_FLASHES:
			self.gun_flashes.append(pg.image.load(path.join("./images/png",img)).convert_alpha())
		self.health_img = pg.image.load("./images/apple.png")
		self.health_img = pg.transform.scale(self.health_img,(TILESIZE,TILESIZE))
		self.bullet_imgs = []
		for bt in BULLET_IMAGES:
			tempimg = pg.image.load(bt)
			tempimg = pg.transform.scale(tempimg,(TILESIZE/4,TILESIZE/4))
			self.bullet_imgs.append(tempimg)
		self.bac_imgs = []
		for bac in BACTERIA_IMAGES:
			tempimg = pg.image.load(bac)
			tempimg = pg.transform.scale(tempimg,(TILESIZE,TILESIZE))
			self.bac_imgs.append(tempimg)
		
	def run(self):
		#Game loop
		
		self.playing = True
		while self.playing:

			self.dt = self.clock.tick(FPS)/1000.0
			#print(self.dt)
			self.events()
			if not self.paused:
				self.update()
			self.draw()	

	def update(self):
		#Game loop - update
		hits = pg.sprite.spritecollide(self.player ,self.bacteria ,False,collide_hit_rect)
		for hit in hits:
			self.player.health -= BAC_TOUCH_DAMAGE*self.dt
			hit.vel = vec(0,0)
			if self.player.health < 0:
				self.playing = False
		hits = pg.sprite.groupcollide(self.bacteria,self.bullets,False,True)
		for hit in hits:
			hit.health-=BAC_HEALTH_RED_MATRIX[hit.type][self.gun_type]    		#BULLET_DAMAGE
			
		hits = pg.sprite.spritecollide(self.player ,self.acid_puddles ,False,collide_hit_rect)
		for hit in hits:
			self.player.health -= ACID_PUDDLE_DAMAGE*self.dt
			if self.player.health < 0:
				self.playing = False

		hits = pg.sprite.spritecollide(self.player ,self.bac_bullets ,False,collide_hit_rect)
		for hit in hits:
			self.player.health -= BAC_BULLET_HEALTH_RED*self.dt
			if self.player.health < 0:
				self.playing = False

		hits = pg.sprite.groupcollide(self.wbc_protect,self.bac_bullets, False,True)
		for hit in hits:
			hit.health -= BULLET_DAMAGE

		if self.player.health < 0.50*PLAYER_HEALTH and not self.healthDone:
			self.health_upgrade = Health_upgrade(self,vec(random.randint(5,15),random.randint(5,15))*TILESIZE)
			self.healthDone = True

		if pg.sprite.collide_rect(self.player,self.health_upgrade):
			self.player.health = 0.70*PLAYER_HEALTH
			self.health_upgrade.kill()
			self.health_upgrade.rect.center = vec(0,0)
		

				
		self.all_sprites.update()
		

	def events(self):
		for event in pg.event.get():
 			if event.type == pg.QUIT:
 				self.playing = False
 				self.running = False
 			if event.type == pg.KEYDOWN:
 				if event.key == pg.K_ESCAPE:
 					pg.quit()
 				if event.key == pg.K_p:
 					self.paused = not self.paused
 				if event.key == pg.K_s:
 					self.gun_type = (self.gun_type+1)%3
 				

 			

	def draw_grid(self):
		for x in range(0,WIDTH,TILESIZE):
			pg.draw.line(self.screen,LIGHTGREY,(x,0),(x,HEIGHT))
		for y in range(0,HEIGHT,TILESIZE):
			pg.draw.line(self.screen,LIGHTGREY,(0,y),(WIDTH,y))
    		

	def draw(self):
		#Game loop - draw
		pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
		self.screen.fill(BGCOLOR)
		#self.draw_grid()
 		#self.screen.blit(self.map_img,self.map_rect)
 		self.all_sprites.draw(self.screen)
 		#pg.draw.rect(self.screen,WHITE,self.player.hit_rect,2)
 		for sprite in self.all_sprites:
 			if isinstance(sprite, Bacteria):
 				sprite.draw_health()
 			self.screen.blit(sprite.image,sprite.rect)
 		#HUD 
 		draw_player_health(self.screen, 10, 10, self.player.health/PLAYER_HEALTH)

 		if self.paused:
 			text_to_screen(self.screen,"ABCDEFGH",0,0)

 		pg.display.flip()


 	


	def show_start_screen(self):
		#game start screen

		pass

	def show_go_screen(self):
		#game over/continue
		pass




g = Game()
g.show_start_screen()

while g.running:
	g.new()
	g.show_go_screen()

pg.quit()