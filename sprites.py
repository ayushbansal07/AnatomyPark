import pygame as pg
from settings import *
from tilemap import collide_hit_rect
from random import uniform, randint, choice
vec = pg.math.Vector2

def collide_with_walls(sprite,group,dir):
	if dir == 'x':
		hits = pg.sprite.spritecollide(sprite,group,False,collide_hit_rect)
		if hits:
			if sprite.vel.x > 0:
				sprite.pos.x = hits[0].rect.left - (sprite.hit_rect.width/2.0)
			elif sprite.vel.x < 0:
				sprite.pos.x = hits[0].rect.right +  (sprite.hit_rect.width/2.0)
			sprite.vel.x = 0
			sprite.hit_rect.centerx = sprite.pos.x

	elif dir == 'y':
		hits = pg.sprite.spritecollide(sprite,sprite.game.walls,False,collide_hit_rect)
		if hits:
			if sprite.vel.y > 0:
				sprite.pos.y = hits[0].rect.top - (sprite.hit_rect.height/2.0)
			elif sprite.vel.y < 0:
				sprite.pos.y = hits[0].rect.bottom + (sprite.hit_rect.height/2.0)
			sprite.vel.y = 0
			sprite.hit_rect.centery = sprite.pos.y



class Player(pg.sprite.Sprite):
	def __init__(self,game,x,y):
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self,self.groups)
		self.game = game
		self.image = self.game.player_img
		
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)
		self.hit_rect = PLAYER_HIT_RECT
		
		#self.vx,self.vy = 0,0
		self.vel = vec(0,0)
		self.pos = vec(x,y)*TILESIZE
		self.rot = 0
		self.rect.center = self.pos
		self.hit_rect.center = self.rect.center
		self.last_shot = 0
		self.health = PLAYER_HEALTH
		#self.x = x*TILESIZE
		#self.y = y*TILESIZE
		self.speed = PLAYER_MAX_SPEED

	def get_keys(self):
		self.rot_speed = 0
		self.vel = vec(0,0)
		keys = pg.key.get_pressed()

		if keys[pg.K_LEFT]:
			self.rot_speed = PLAYER_ROT_SPEED
			#print(keys[pg.K_LEFT])
		if keys[pg.K_RIGHT]:
			self.rot_speed = -PLAYER_ROT_SPEED
		if keys[pg.K_UP]:
			self.vel = vec(self.speed,0).rotate(-self.rot)
		if keys[pg.K_DOWN]:
			self.vel = -vec(self.speed/2.0,0).rotate(-self.rot)
		if keys[pg.K_SPACE]:
			now = pg.time.get_ticks()
			if now - self.last_shot > BULLET_RATE:
				self.last_shot = now
				direction = vec(1,0).rotate(-self.rot)
				pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
				Bullet(self.game,self.pos,direction)
				self.vel = vec(-KICKBACK,0).rotate(-self.rot)
				MuzzleFlash(self.game,pos)

			



	
	def update(self):
		self.speed = min(self.speed+PLAYER_SPEED_RESTORE_RATE*self.game.dt,PLAYER_MAX_SPEED)

		self.get_keys()
		self.rot = (self.rot + self.rot_speed*self.game.dt) % 360
		self.image = pg.transform.rotate(self.game.player_img, self.rot)
		self.rect = self.image.get_rect()
		self.rect.center = self.pos
		self.hit_rect.center = self.pos

		self.pos += self.vel*self.game.dt
		
		
		self.hit_rect.centerx = self.pos.x
		collide_with_walls(self,self.game.walls,'x')
		
		
		

		self.hit_rect.centery = self.pos.y
		collide_with_walls(self,self.game.walls,'y')
		self.rect.center = self.hit_rect.center
	
	



		

class Wall(pg.sprite.Sprite):
	def __init__(self, game, x, y):
		self.groups = game.all_sprites, game.walls
		pg.sprite.Sprite.__init__(self,self.groups)
		self.game = game
		self.image = game.wall_img
		#self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.rect.x = x*TILESIZE
		self.rect.y = y*TILESIZE

class Acid_Puddle(pg.sprite.Sprite):
	def __init__(self, game, x, y):
		self.groups = game.all_sprites, game.acid_puddles
		pg.sprite.Sprite.__init__(self,self.groups)
		self.game = game
		self.image = game.puddle_img
		#self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.rect.x = x*TILESIZE
		self.rect.y = y*TILESIZE



class Bacteria(pg.sprite.Sprite):
	def __init__(self, game, x, y):
		self.groups = game.all_sprites, game.bacteria
		pg.sprite.Sprite.__init__(self,self.groups)
		self.game = game
		self.image = game.bac_img
		#self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		self.pos = vec(x,y)*TILESIZE
		self.rect.center = self.pos
		self.rot = 0
		self.vel = (0,0)
		self.acc = (0,0)
		self.hit_rect = BAC_HIT_RECT.copy()
		self.hit_rect.center = self.rect.center
		self.health = BAC_HEALTH
		self.last_shot = 0

		
	def avoid_bacteria(self):
		for bacteria in self.game.bacteria:
			if bacteria!=self:
				dist = self.pos - bacteria.pos
				if 0 < dist.length() < BAC_AVOID_RADIUS:
					self.acc +=dist.normalize()

	def fire_bullets_on_player(self):
		player_rot = self.game.player.rot
		my_vector = self.pos-self.game.player.pos
		my_angle = my_vector.angle_to(vec(1,0).rotate(-player_rot))
		if -30 < my_angle and my_angle < 30:
			#ran = uniform(0,1)
			now = pg.time.get_ticks()
			if now - self.last_shot > BAC_BULLET_RATE:
				self.last_shot = now
				direction = vec(1,0).rotate(-self.rot)
				pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
				Bac_Bullet(self.game,self.pos,direction)
				#self.vel = vec(-KICKBACK,0).rotate(-self.rot)
			
	
	def avoid_bullets(self):
		for bullet in self.game.bullets:
			bul_rot = bullet.rot
			my_vector = self.pos - bullet.pos
			my_angle = my_vector.angle_to(vec(1,0).rotate(-bul_rot))
			if -30 < my_angle and my_angle < 30:
			#ran = uniform(0,1)
				self.acc = vec(0,0)
				if my_angle > 0:
					self.acc += (vec(1,0).rotate(-bul_rot-90))
				else:
					self.acc += (vec(1,0).rotate(-bul_rot+90))



	def update(self):
		self.rot = (self.game.player.pos - self.pos).angle_to(vec(1,0))
		self.image = pg.transform.rotate(self.game.bac_img,self.rot)
		self.rect = self.image.get_rect()
		self.rect.center = self.pos
		self.acc = vec(1,0).rotate(-self.rot)
		self.avoid_bacteria()
		self.avoid_bullets()
		self.fire_bullets_on_player()
		self.acc.scale_to_length(BAC_SPEED)
		self.acc -= self.vel 
		self.vel += self.acc * self.game.dt
		self.pos += self.vel * self.game.dt + 0.5*self.acc * (self.game.dt)**2
		self.hit_rect.centerx = self.pos.x
		collide_with_walls(self,self.game.walls,'x')
		self.hit_rect.centery = self.pos.y
		collide_with_walls(self,self.game.walls,'y')
		self.rect.center = self.hit_rect.center
		if(self.health<=0):
			self.kill()

	def draw_health(self):
		if self.health > 0.6*BAC_HEALTH:
			col = GREEN
		elif self.health > 0.3 * BAC_HEALTH:
			col = YELLOW
		else : 
			col = RED 

		width = int(self.rect.width*self.health/BAC_HEALTH)
		self.health_bar = pg.Rect(0, 0, width, 7)
		if self.health < BAC_HEALTH : 
			pg.draw.rect(self.image,col,self.health_bar)	


class Bullet(pg.sprite.Sprite):
	def __init__(self, game, pos, dir):
		self.groups = game.all_sprites,game.bullets
		pg.sprite.Sprite.__init__(self,self.groups)
		self.image = game.bullet_img
		self.rect = self.image.get_rect()
		self.pos = vec(pos)
		self.rect.center = vec(pos)
		spread = uniform(-GUN_SPREAD,GUN_SPREAD)
		self.rot = dir.angle_to(vec(1,0))
		self.vel = dir.rotate(0) * BULLET_SPEED
		self.spawn_time = pg.time.get_ticks()
		self.game = game

	def update(self):
		self.pos += self.vel * self.game.dt
		self.rect.center = self.pos
		if pg.sprite.spritecollideany(self,self.game.walls):
			self.kill()
		if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
			self.kill()

class Bac_Bullet(pg.sprite.Sprite):
	def __init__(self, game, pos, dir):
		self.groups = game.all_sprites,game.bac_bullets
		pg.sprite.Sprite.__init__(self,self.groups)
		self.image = game.bullet_img
		self.rect = self.image.get_rect()
		self.pos = vec(pos)
		self.rect.center = vec(pos)
		spread = uniform(-GUN_SPREAD,GUN_SPREAD)
		self.rot = dir.angle_to(vec(1,0))
		self.vel = dir.rotate(0) * BAC_BULLET_SPEED
		self.spawn_time = pg.time.get_ticks()
		self.game = game

	def update(self):
		self.pos += self.vel * self.game.dt
		self.rect.center = self.pos
		if pg.sprite.spritecollideany(self,self.game.walls):
			self.kill()
		if pg.time.get_ticks() - self.spawn_time > BAC_BULLET_LIFETIME:
			self.kill()

class MuzzleFlash(pg.sprite.Sprite):
	def __init__(self,game,pos):
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self,self.groups)
		self.game = game
		size = randint(10,25)
		self.image = pg.transform.scale(choice(game.gun_flashes),(size,size))
		self.rect = self.image.get_rect()
		self.pos = pos 
		self.rect.center = pos
		self.spawn_time = pg.time.get_ticks()

	def update(self):
		if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
			self.kill()

class WBC_protect(pg.sprite.Sprite):
	def __init__(self,game,x,y,cover):
		self.groups = game.all_sprites, game.wbc_protect 
		pg.sprite.Sprite.__init__(self,self.groups)
		self.game = game
		self.image = game.wbc_img
		self.rect = self.image.get_rect()
		self.pos = vec(x,y)*TILESIZE
		self.rect.center = self.pos
		
		self.health = 50
		self.cover = cover
		self.rot = 0
		self.vel = (0,0)
		self.acc = (0,0)
		self.hit_rect = BAC_HIT_RECT.copy()
		self.hit_rect.center = self.rect.center
		#self.health = BAC_HEALTH

	def arrive(self,target):
		self.rot = (target - self.pos).angle_to(vec(1,0))
		self.image = pg.transform.rotate(self.game.wbc_img,self.rot)
		self.rect = self.image.get_rect()
		self.rect.center = self.pos
		self.acc = vec(1,0).rotate(-self.rot)
		

	def avoid_wbc_and_player(self):
		for wbc in self.game.wbc_protect:
			if wbc!=self:
				dist = self.pos - wbc.pos
				if 0 < dist.length() < WBC_AVOID_RADIUS:
					self.acc +=dist.normalize()
		dist = self.pos - self.game.player.pos
		if 0< dist.length() < WBC_AVOID_RADIUS:
			self.acc += dist.normalize()

	def update(self):
		target = self.game.player.pos
		if(self.cover == 1):
			self.arrive(target+(0,-TILESIZE))
		if(self.cover == 2):
			self.arrive(target+(0,+TILESIZE))
		if(self.cover == 3):
			self.arrive(target+(-TILESIZE,-TILESIZE))
		if(self.cover == 4):
			self.arrive(target+(+TILESIZE,-TILESIZE))
		if(self.cover == 5):
			self.arrive(target+(-TILESIZE,+TILESIZE))
		if(self.cover == 6):
			self.arrive(target+(+TILESIZE,+TILESIZE))
		if(self.cover == 7):
			self.arrive(target+(TILESIZE,0))
		if(self.cover == 8):
			self.arrive(target+(-TILESIZE,0))
		self.avoid_wbc_and_player()
		self.acc.scale_to_length(WBC_SPEED)
		self.acc -= self.vel 
		self.vel += self.acc * self.game.dt
		self.pos += self.vel * self.game.dt + 0.5*self.acc * (self.game.dt)**2
		self.hit_rect.centerx = self.pos.x
		collide_with_walls(self,self.game.walls,'x')
		self.hit_rect.centery = self.pos.y
		collide_with_walls(self,self.game.walls,'y')
		self.rect.center = self.hit_rect.center
		if(self.health<=0):
			self.kill()

class WBC_attack(pg.sprite.Sprite):
	def __init__(self,game,pos):
		self.groups = game.all_sprites, game.wbc_attack
		pg.sprite.Sprite.__init__(self,self.groups)
		self.game = game
		self.rect = self.image.get_rect()
		self.pos = pos 
		self.rect.center = pos
		self.image = game.bullet_img

	def update(self):
		pass