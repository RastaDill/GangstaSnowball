#!/usr/bin/python
#  gangsta.py
#  
#  Copyright (C) 2015 Voznesensky (WeedMan) Michael <weedman@opmbx.org>
#
#  Gangsta Snowball for Gamiron #11

import os

from cocos.director import director
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.layer import Layer, ScrollingManager, ScrollableLayer, ColorLayer
from cocos.text import Label
from cocos.tiles import load, RectMapCollider
from cocos.sprite import Sprite
from cocos.actions import *
from cocos.audio.effect import Effect

import cocos.audio.pygame.music as Music
import cocos.collision_model as cm

from pyglet.window import key, ImageMouseCursor
from pyglet import image
from pyglet import font

import pyglet.resource

import math

font.add_file(os.path.join('PTSans','PTN57F.ttf'))
name_font = font.load('PT Sans Narrow')

const = {"rect_up": 16,
		"life_ball": 2,
		"number_taps": 25,
		"duration_kit_effect": 5,
		"gangsta":{"speed": 250,
					"speed_sball": 350,
					"interval_throw": 0.5,
					"font_color": (91,64,40,255)},
		"kid":{"speed_ox": 180,
				"speed_oy": 230,
				"speed_sball": 300,
				"speed_checkball": 2000,
				"interval_throw": 1.5},
		"grandfa":{"font_color": (107,63,122,255)},
		"font_name": 'PT Sans Narrow'}

class BallSprite(Sprite):
	"""Basic concept Sprite and this class use sball"""
	def __init__(self, image, position = (0, 0)):
		super(BallSprite, self).__init__(image, position)
		
		self.cshape = cm.AARectShape(position, self.width/2, self.height/2)
		self.counter = 0 #special counter
	
	def update_cshape(self):
		self.cshape.center = self.x, self.y
		self.counter += 1

class GangstaLegs(Sprite):
	def __init__(self, image, position, rotation):
		super(GangstaLegs, self).__init__(image, position, rotation)
		self.position = position
		self.rotation = rotation
	
	def update(self, position, rotation):
		self.position = position
		self.rotation = rotation

class GangstaSprite(BallSprite):
	"""Class Sprite for gangsta"""
	def __init__(self, image, position = (0, 0)):
		super(GangstaSprite, self).__init__(image, position)
		
		self.cshape = cm.AARectShape(position, self.width/2, self.height/2)
		self.freeze = False
		self.img_sball = None #name or path to image snowball
		self.interval_throw = 0
		self.near_obj = None
		self.where_near_obj = None
		self.allthrow_ball = [] #all throw ball
	
	def update_cshape(self):
		self.cshape.center = self.position
		self.counter += 1

class KidSprite(GangstaSprite):
	"""Class Sprite for kid (enemy)"""
	def __init__(self, image, position = (0, 0)):
		super(KidSprite, self).__init__(image, position)
		
		self.health = 100 #health
		self.can_move = False
		self.can_throw = False
		self.speed_indicator = 1

class GangstaMove(Action, RectMapCollider):
	"""Gagsta move"""
	def __init__(self, current_map, rect_up = 0):
		super(GangstaMove, self).__init__()
		
		self.rect_up = rect_up
		self.current_map = current_map
	
	def rotation(self):
		rotation = self.target.rotation * math.pi/180.0 #conversion on rad
		return math.sin(rotation), math.cos(-rotation)
	
	def check_rect(self, last_rect, new_rect, near_rect):
		if last_rect.bottom + self.rect_up >= near_rect.top + self.rect_up and new_rect.bottom < near_rect.top + self.rect_up:
			new_rect.bottom = near_rect.top + self.rect_up
			self.target.where_near_obj = "bottom"
		if last_rect.right - self.rect_up <= near_rect.left - self.rect_up and new_rect.right > near_rect.left - self.rect_up:
			new_rect.right = near_rect.left - self.rect_up
			self.target.where_near_obj = "right"
		if last_rect.left + self.rect_up >= near_rect.right + self.rect_up and new_rect.left < near_rect.right + self.rect_up:
			new_rect.left = near_rect.right + self.rect_up
			self.target.where_near_obj = "left"
		if last_rect.top - self.rect_up <= near_rect.bottom - self.rect_up and new_rect.top > near_rect.bottom - self.rect_up:
			new_rect.top = near_rect.bottom - self.rect_up
			self.target.where_near_obj = "top"
		return new_rect
	
	def move_target(self, dx, dy):
		
		last_rect = self.target.get_rect()
		last_rect.midleft = last_rect.x, self.target.y
		new_rect = last_rect.copy()
		
		new_rect.x += dx
		new_rect.y += dy
		
		if new_rect != last_rect:
			self.target.parent.add_animation()
		else: self.target.parent.remove_animation()
		
		if self.target.near_obj is not None:
			if str(type(self.target.near_obj)) == "<type 'list'>":
				for near in self.target.near_obj:
					if near != self.target:
						near_rect = near.get_rect()
						new_rect = self.check_rect(last_rect, new_rect, near_rect)
			else:
				near_rect = self.target.near_obj.get_rect()
				new_rect = self.check_rect(last_rect, new_rect, near_rect)
		
		dx, dy = self.collide_map(list_map[self.current_map], last_rect, new_rect, dy, dx)
		
		return new_rect.center
	
	def step(self, dt):
		if not self.target.freeze:
			rotation_x, rotation_y = self.rotation()
			
			# velocity UP or DOWN
			velocity_x1, velocity_y1 = (keyboard[key.W] - keyboard[key.S]) * const["gangsta"]["speed"] * dt * rotation_x,\
										(keyboard[key.W] - keyboard[key.S]) * const["gangsta"]["speed"] * dt * rotation_y
			#velocity LEFT or RIGHT
			velocity_x2, velocity_y2 = (keyboard[key.D] - keyboard[key.A]) * const["gangsta"]["speed"] * dt * rotation_y,\
										(keyboard[key.A] - keyboard[key.D]) * const["gangsta"]["speed"] * dt * rotation_x
			
			self.target.position = self.move_target(velocity_x1 + velocity_x2, velocity_y1 + velocity_y2)
			
			list_sm[self.current_map].set_focus(*self.target.position)
		else: self.target.parent.remove_animation()

class KidMove(GangstaMove):
	"""Kid move"""
	def __init__(self, current_map, rect_up):
		super(KidMove, self).__init__(current_map, rect_up)
		
		self.velocity_x1, self.velocity_y1 = 0, 0
		self.velocity_x2, self.velocity_y2 = 0, 0
	
	def step(self, dt):
		
		if self.target.can_move and not self.target.freeze:
			
			rotation_x, rotation_y = self.rotation()
			
			# velocity UP or DOWN
			self.velocity_x1, self.velocity_y1 = self.target.speed_indicator * const["kid"]["speed_oy"] * dt * rotation_x,\
													self.target.speed_indicator * const["kid"]["speed_oy"] * dt * rotation_y
			#velocity LEFT or RIGHT
			if keyboard[key.A] or keyboard[key.D]:
				self.velocity_x2, self.velocity_y2 = self.target.speed_indicator * const["kid"]["speed_ox"] * dt * rotation_y,\
														self.target.speed_indicator * const["kid"]["speed_ox"] * dt * rotation_x
			else:
				self.velocity_x2, self.velocity_y2 = 0, 0
			
			self.target.position = self.move_target(self.velocity_x1 + self.velocity_x2, self.velocity_y1 + self.velocity_y2)

class SnowballMove(Action, RectMapCollider):
	"""Snowball move"""
	def __init__(self, rotation, speed, current_map):
		super(SnowballMove, self).__init__()
		
		self.current_map = current_map
		
		self.rotation = rotation * math.pi/180.0
		self.speed = speed
	
	def step(self, dt):
		dx = math.sin(self.rotation) * self.speed * dt
		dy = math.cos(-self.rotation) * self.speed * dt
		
		last_rect = self.target.get_rect()
		new_rect = last_rect.copy()
		
		new_rect.x += dx
		new_rect.y += dy
		
		self.target.velocity = self.collide_map(list_map[self.current_map], last_rect, new_rect, dy, dx)
		if self.target.velocity != (dx, dy) or self.target.counter//60 > const["life_ball"]:
			self.target.parent.remove_sball(self.target)
		
		self.target.position = new_rect.center
		self.target.update_cshape()

class MainLayer(ScrollableLayer, RectMapCollider):
	"""Main layer in Game"""
	is_event_handler = True
	
	def __init__(self, current_map):
		super(MainLayer, self).__init__()
		
		self.current_map = current_map
		
		#create nedeed collision manager
		self.cm_gball = cm.CollisionManagerBruteForce()
		self.cm_kball = cm.CollisionManagerBruteForce()
		self.cm_gangsta = cm.CollisionManagerBruteForce()
		self.cm_kids = cm.CollisionManagerBruteForce()
		
		#create kids
		try:
			self.kids_start = list_map[self.current_map].find_cells(kid_start = True)
		except: self.kids_start = None
		if self.kids_start is not None:
			self.list_kids = []
			for i in range(len(self.kids_start)):
				kid = KidSprite(os.path.join('img','kid.png'))
				kid.position = self.__set_position(kid, self.kids_start[i])
				self.add(kid, z=1)
				kid.interval_throw = const["kid"]["interval_throw"]
				kid.img_sball = os.path.join('img','kb.png')
				self.list_kids.append(kid)
				kid.do(KidMove(self.current_map, const["rect_up"]))
		
		#create gangsta
		self.gangsta_start = list_map[self.current_map].find_cells(gangsta_start = True)[0]
		self.gangsta = GangstaSprite(os.path.join('img','gangsta.png'))
		self.gangsta.position = self.__set_position(self.gangsta, self.gangsta_start)
		self.add(self.gangsta, z=1)
		self.gangsta.interval_throw = const["gangsta"]["interval_throw"]
		self.gangsta.img_sball = os.path.join('img','gb.png')
		self.cm_gangsta.add(self.gangsta)
		self.gangsta.do(GangstaMove(self.current_map))
		
		self.gangsta_legs = GangstaLegs(gangsta_mo, self.gangsta.position, self.gangsta.rotation)
		self.gangsta_legs_add = False
		
		#create point transition
		try:
			self.transition_start = list_map[self.current_map].find_cells(transition = True)[0]
		except: self.transition_start = None
		if self.transition_start is not None:
			self.counter_taps = 0 # counter pressed key E
			self.transition = BallSprite(os.path.join('img','transition_1.png'), (200, 300))
			self.transition.position = self.__set_position(self.transition, self.transition_start)
			self.add(self.transition)
		
		#create mediacal kit
		try:
			self.kit_start = list_map[self.current_map].find_cells(kit = True)[0]
		except:
			self.kit_start = None
		if self.kit_start is not None:
			self.slow_mo = False
			self.count_mo = 0
			self.mediacal_kit = BallSprite(os.path.join('img','kit.png'), (200, 200))
			self.mediacal_kit.position = self.__set_position(self.mediacal_kit, self.kit_start)
			self.add(self.mediacal_kit)
		
		self.mous_x, self.mous_y = 0, 0
		self.change_gangsta = 0
		
		self.schedule(self.update)
	
	def on_mouse_motion(self, mx, my, dx, dy):
		self.mous_x, self.mous_y = director.get_virtual_coordinates(mx, my)
	
	def on_mouse_press(self, x, y, button, modifiers):
		if button == 1 and not self.gangsta.freeze:
			self.change_gangsta = 1
			self.gangsta.image = pyglet.resource.image(os.path.join('img','gangsta_shoot.png'))
			self.__throw_snowball(self.gangsta, const["gangsta"]["speed_sball"])
	
	def on_key_press(self, k, mod):
		if k == key.E and self.transition_start is not None:
			if self.cm_gangsta.any_near(self.transition, 10) and self.counter_taps < const["number_taps"]:
				self.counter_taps += 1
				if self.counter_taps == 9:
					self.transition.image = pyglet.resource.image(os.path.join('img','transition_2.png'))
				elif self.counter_taps == 17:
					self.transition.image = pyglet.resource.image(os.path.join('img','transition_3.png'))
				elif self.counter_taps == const["number_taps"]:
					self.transition.image = pyglet.resource.image(os.path.join('img','transition_4.png'))
	
	def remove_sball(self, sball):
		"""Remove all ball touched barrier"""
		if sball in self.gangsta.allthrow_ball:
			self.gangsta.allthrow_ball.remove(sball)
			sball.kill()
		else:
			for kid in self.list_kids:
				if sball in kid.allthrow_ball:
					if math.sqrt((kid.x-sball.x)**2 + (kid.y-sball.y)**2) + 90 >=\
						math.sqrt((kid.x-self.gangsta.x)**2 + (kid.y-self.gangsta.y)**2):
							kid.can_throw = True
					else:
						kid.can_throw = False
					
					kid.allthrow_ball.remove(sball)
					sball.kill()
	
	def add_animation(self):
		self.gangsta_legs.update(self.gangsta.position, self.gangsta.rotation)
		if not self.gangsta_legs_add:
			self.add(self.gangsta_legs)
			self.gangsta_legs_add = True
	
	def remove_animation(self):
		if self.gangsta_legs_add:
			self.remove(self.gangsta_legs)
			self.gangsta_legs_add = False
	
	def __set_position(self, obj, cell):
		"""Set position object in cell"""
		rect_obj = obj.get_rect()
		rect_obj.center = cell.center
		return rect_obj.center
	
	def __rotation(self, obj_rot, about_x, about_y):
		"""Find out the angle of rotation of the sprite about x and y another coordinate"""
		try:
			angle_rotation = math.atan((obj_rot.x-about_x)/(obj_rot.y-about_y)) * 180.0/math.pi
			if about_y <= obj_rot.y:
				angle_rotation += 180
		except ZeroDivisionError:
			if about_x > obj_rot.x:
				angle_rotation = 90
			else:
				angle_rotation = -90
		
		return angle_rotation
	
	def __throw_snowball(self, obj_throw, speed, special_img = False):
		"""Throw snowball about obj_throw"""
		if special_img:
			if obj_throw.counter//30 > 0.01:
				sball = BallSprite(os.path.join('img','check.png'), (obj_throw.position))
				sball.do(SnowballMove(self.__rotation(obj_throw, self.gangsta.x, self.gangsta.y), speed, self.current_map))
		else:
			if obj_throw.counter//15 > obj_throw.interval_throw:
				if obj_throw.interval_throw == const["gangsta"]["interval_throw"]:
					shootgun.play()
					ag = self.gangsta.rotation*math.pi/180
					sball = BallSprite(obj_throw.img_sball, (self.gangsta.position[0]+(40 * math.sin(ag)), self.gangsta.position[1]+(40 * math.cos(-ag))))
				else:
					throw_kid.play()
					sball = BallSprite(obj_throw.img_sball, (obj_throw.position))
				sball.do(SnowballMove(obj_throw.rotation, speed, self.current_map))
		try:
			self.add(sball, z=0)
			obj_throw.allthrow_ball.append(sball)
			obj_throw.counter = 0
		except NameError: pass
	
	def __restart(self):
		"""Returns all units to their original positions and resets all of their settings"""
		global vitality
		#restart for gangsta
		self.gangsta.position = self.__set_position(self.gangsta, self.gangsta_start)
		vitality = 100
		self.gangsta.color = (255, 255, 255)
		self.gangsta.freeze = False
		for sball in self.gangsta.allthrow_ball:
			self.gangsta.allthrow_ball.remove(sball)
			sball.kill()
		
		#reset for kids
		if self.kids_start is not None:
			for kid in self.list_kids:
				kid.position = self.__set_position(kid, self.kids_start[self.list_kids.index(kid)])
				kid.freeze = False
				kid.color = (255,255,255)
				kid.health = 100
				kid.can_move = False
				kid.can_throw = False
				for sball in kid.allthrow_ball:
					kid.allthrow_ball.remove(sball)
					sball.kill()
		
		#reset for transition
		if self.transition_start is not None:
			self.counter_taps = 0
			self.transition.image = pyglet.resource.image(os.path.join('img','transition_1.png'))
		
		#reset for medical kit
		if self.kit_start is not None:
			self.slow_mo = False
			self.count_mo = 0
			self.add(self.mediacal_kit)
	
	def __slow(self, speed_oy, speed_ox, speed_sball, interval_throw):
		"""Slowed or recovery kids then take kit"""
		global const
		const["kid"]["speed_oy"] = speed_oy
		const["kid"]["speed_ox"] = speed_ox
		const["kid"]["speed_sball"] = speed_sball
		if self.kids_start is not None:
			for kid in self.list_kids:
				kid.interval_throw = interval_throw
	
	def update(self, dt):
		"""Main loop"""
		global vitality, first_kit
		
		if vitality == 0:
			self.gangsta.color = (20,50,200)
			self.gangsta.freeze = True
		
		#remove gun gangsta
		if self.change_gangsta > 0:
			self.change_gangsta += 1
			if self.change_gangsta//60 > 2:
				self.gangsta.image = pyglet.resource.image(os.path.join('img','gangsta.png'))
				self.change_gangsta = 0
		
		if self.kit_start is not None:
			if self.slow_mo and self.count_mo == 0:
				self.__slow(180, 90, 210, 3)
				self.count_mo +=1
			if self.count_mo > 0:
				self.count_mo += 1
				if self.count_mo//60 > const["duration_kit_effect"]:
					self.__slow(230, 180, 300, 1.5)
					self.count_mo = -1
		
		if self.kids_start is not None:
			for kid in self.list_kids:
				#checks the proximity of children
				kid_near = self.cm_kids.any_near(kid, 20)
				if kid_near:
					kid.near_obj = self.list_kids
				else: kid.near_obj = None
				
				#if gangsta near, then kid shoot him
				action_kid = self.cm_gangsta.any_near(kid, 500)
				if action_kid and not kid.freeze:
					if not kid.can_throw:
						#check whether there is obstacle between the child and the gangster
						self.__throw_snowball(kid, const["kid"]["speed_checkball"], special_img = True)
					else:
						kid.rotation = self.__rotation(kid, self.gangsta.x, self.gangsta.y)
						self.__throw_snowball(kid, const["kid"]["speed_sball"])
						#if gangsta is too close to the kid away from him
						if self.cm_gangsta.any_near(kid, 80):
							if not kid.can_move:
								kid.can_move = True
								kid.image = kid_mo
							kid.speed_indicator = -1
						#if the distance is acceptable, then the kid is not moving
						elif self.cm_gangsta.any_near(kid, 100):
							kid.can_move = False
							kid.image = pyglet.resource.image(os.path.join('img','kid.png'))
						else:
							if not kid.can_move:
								kid.can_move = True
								kid.image = kid_mo
							kid.speed_indicator = 1
				else:
					kid.can_move = False
					if kid.freeze and kid.counter//60 > 4:
						broken.play()
						kid.freeze = False
						kid.color = (255,255,255)
						kid.health = 100
		
		if not self.gangsta.freeze:
			self.gangsta.rotation = self.__rotation(self.gangsta, self.view_x + self.mous_x, self.view_y + self.mous_y)
			if keyboard[key.SPACE]:
				self.__throw_snowball(self.gangsta, const["gangsta"]["speed_sball"])
		
		self.cm_gangsta.clear()
		self.cm_kids.clear()
		self.cm_gball.clear()
		self.cm_kball.clear()
		
		self.cm_gangsta.add(self.gangsta)
		for sball in self.gangsta.allthrow_ball:
			self.cm_gball.add(sball)
		
		if self.kids_start is not None:
			for kid in self.list_kids:
				self.cm_kids.add(kid)
		
			for kid in self.list_kids:
				#gangsta got kid
				colliding_gball = self.cm_gball.objs_colliding(kid)
				if colliding_gball:
					snowg.play()
					if kid.health:
						kid.health -= 25 #damage
					else:
						kid.color = (100,100,255)
						crystallization.play()
						kid.freeze = True
						kid.image = pyglet.resource.image(os.path.join('img','kid.png'))
						kid.counter = 0
					for gb in colliding_gball:
						self.remove_sball(gb)
				
				for kb in kid.allthrow_ball:
					#kid got gangsta
					if self.cm_kball.they_collide(kb, self.gangsta):
						if kid.can_throw:
							snowk.play()
							if vitality > 10:
								vitality -= 10 #damage
							elif vitality > 1:
								vitality -= 9
							elif vitality == 1:
								vitality -= 1
								self.gangsta.color = (20,50,200)
								crystallization.play()
								self.gangsta.freeze = True
						self.remove_sball(kb)
		
		if self.kit_start is not None:
			if self.cm_gangsta.objs_colliding(self.mediacal_kit) and not self.slow_mo:
				if first_kit is None: first_kit = True
				self.slow_mo = True
				self.remove(self.mediacal_kit)
				vitality = 100
				liquid_normal = Liquid(waves=10, amplitude=30, grid=(16,16), duration=const["duration_kit_effect"])
				liquid = AccelDeccelAmplitude(liquid_normal, rate = 0.5)
				list_level[self.current_map].do(liquid + StopGrid())
			
			self.mediacal_kit.update_cshape()
		
		
		if self.transition_start is not None:
			if self.cm_gangsta.any_near(self.transition, 10) and self.counter_taps < const["number_taps"]:
				self.gangsta.near_obj = self.transition
			else:
				self.gangsta.near_obj = None
				if self.gangsta.where_near_obj == "bottom":
					if self.gangsta.y < self.transition.y:
						self.gangsta.where_near_obj = None
						director.replace(SlideInTTransition(list_level[self.current_map+1]))
				elif self.gangsta.where_near_obj == "top":
					if self.gangsta.y > self.transition.y:
						self.gangsta.where_near_obj = None
						director.replace(SlideInBTransition(list_level[self.current_map+1]))
				if self.gangsta.where_near_obj == "right":
					if self.gangsta.x > self.transition.x:
						self.gangsta.where_near_obj = None
						director.replace(SlideInLTransition(list_level[self.current_map+1]))
				if self.gangsta.where_near_obj == "left":
					if self.gangsta.x < self.transition.x:
						self.gangsta.where_near_obj = None
						director.replace(SlideInRTransition(list_level[self.current_map+1]))
			
			self.transition.update_cshape()
		
		self.gangsta.update_cshape()
		
		if self.kids_start is not None:
			for kid in self.list_kids:
				kid.update_cshape()
		
		if keyboard[key.R]:
			self.__restart()

class FinalLayer(Layer):
	def __init__(self):
		super(FinalLayer, self).__init__()
		self.gangsta = Sprite(os.path.join('img','gangsta.png'), position = (400, 250))
		self.add(self.gangsta)
		
		self.grandfa = Sprite(os.path.join('img','grandfa.png'), position = (400, 350) )
		self.add(self.grandfa)
		
		self.grandfa_rep1 = Label("Where f*ck you walk? Again with his buddies smoked weed?",
								font_size = 25,
								font_name = const["font_name"],
								anchor_x = 'left', anchor_y = 'center',
								color = const["grandfa"]["font_color"],
								position = (100, 450))
		self.grandfa_rep2 = Label("No matter. Let's go to the orphanage",
								font_size = 25,
								font_name = const["font_name"],
								anchor_x = 'left', anchor_y = 'center',
								color = const["grandfa"]["font_color"],
								position = (100, 450))
		self.grandfa_rep3 = Label("Children need to hand out gifts",
								font_size = 25,
								font_name = const["font_name"],
								anchor_x = 'left', anchor_y = 'center',
								color = const["grandfa"]["font_color"],
								position = (100, 450))
		
		self.gangsta_rep1 = Label("No no no. Just in the park ... kids ...",
								font_size = 25,
								font_name = const["font_name"],
								anchor_x = 'left', anchor_y = 'center',
								color = const["gangsta"]["font_color"],
								position = (100, 150))
		
		self.happy = Label("Happy New Year 2016!!!",
							font_size = 40,
							font_name = const["font_name"],
							anchor_x = 'center', anchor_y = 'center',
							color = (255, 0, 0, 255),
							position = (400, 300))
		
		self.for_gamiron = Label("special for Gamiron#11",
									font_name = const["font_name"],
									font_size = 20,
									anchor_x = 'center', anchor_y = 'center',
									color = (30,30,30,255),
									position = (400, 200))
		
		self.list_rep = [self.grandfa_rep1, self.gangsta_rep1, self.grandfa_rep2, self.grandfa_rep3, self.happy]
		
		self.schedule(self.update)
		
		self.delay_replica = 0
		self.index_rep = 0
		
		self.schedule(self.update)
	
	def update(self, dt):
		if (self.delay_replica//60>10 and self.index_rep < len(self.list_rep)) or self.index_rep == 0:
			self.delay_replica = 1
			self.add(self.list_rep[self.index_rep])
			if self.index_rep != 0:
				if self.index_rep == len(self.list_rep)-1:
					self.remove(self.gangsta)
					self.remove(self.grandfa)
					self.add(self.for_gamiron)
				self.remove(self.list_rep[self.index_rep-1])
			self.index_rep += 1
		self.delay_replica +=1

class TextLayer(Layer):
	def __init__(self):
		super(TextLayer, self).__init__()
		
		self.gangsta_health = Label(str(vitality),
									font_name = const["font_name"],
									font_size = 32,
									anchor_x = 'center', anchor_y = 'center',
									color = (255,50,50,255),
									position = (80, 80))
		self.add(self.gangsta_health)
		
		self.for_gamiron = Label("special for Gamiron#11",
									font_name = const["font_name"],
									font_size = 15,
									anchor_x = 'left', anchor_y = 'center',
									color = (50,50,50,180),
									position = (20, 580))
		self.add(self.for_gamiron)
		
		self.reload_key = Label("R - reload level",
								font_name = const["font_name"],
								font_size = 15,
								anchor_x = 'left', anchor_y = 'center',
								color = (50,50,50,180),
								position = (20, 40))
		self.continue_key = Label("E - multiple presses to clean the road",
									font_name = const["font_name"],
									font_size = 15,
									anchor_x = 'left', anchor_y = 'center',
									color = (50,50,50,180),
									position = (20, 20))
		self.add(self.reload_key)
		self.add(self.continue_key)
		
		self.nice_shit = Label("Wow... nice shit",
								font_name = const["font_name"],
								font_size = 30,
								anchor_x = 'center', anchor_y = 'center',
								color = const["gangsta"]["font_color"],
								position = (400, 80))
		
		self.schedule(self.update)
		
		self.delay_text = 0
	
	def update(self, dt):
		global first_kit
		if first_kit and self.delay_text == 0:
			self.add(self.nice_shit)
			first_kit = False
			self.delay_text += 1
		
		if self.delay_text > 0:
			self.delay_text += 1
		
		if self.delay_text//60>2:
			self.delay_text = 0
			self.remove(self.nice_shit)
		
		self.gangsta_health.element.text = str(vitality)
		

#width=1280, height=720, 
director.init(width=800, height=600, caption = "Gangsta Snowball (for Gamiron#11)", audio_backend='sdl', autoscale=False, resizable=True)
#lisen keyboard event
keyboard = key.KeyStateHandler()
director.window.push_handlers(keyboard)
#set image cursor
image = image.load(os.path.join('img','aim.png'))
cursor = ImageMouseCursor(image, 8, 8)
director.window.set_mouse_cursor(cursor)

###resourse###
shootgun = Effect(os.path.join('sound','shoot.wav'))
throw_kid = Effect(os.path.join('sound','throw_kid.ogg'))
snowg = Effect(os.path.join('sound','snowg.wav'))
snowk = Effect(os.path.join('sound','snowk.wav'))
crystallization = Effect(os.path.join('sound','crist.ogg'))
broken = Effect(os.path.join('sound','broken.ogg'))
Music.load(os.path.join('sound','hip-hop.wav'))
Music.play(loops = -1)

image_gangsta_frame = (os.path.join('img','legs_1.png'),
						os.path.join('img','legs_2.png'),
						os.path.join('img','legs_3.png'),
						os.path.join('img','legs_4.png'))
images_gangsta_mo = map(lambda img: pyglet.image.load(img), image_gangsta_frame)
gangsta_mo = pyglet.image.Animation.from_image_sequence(images_gangsta_mo, 0.1)

image_kid_frame = (os.path.join('img','kid_1.png'),
					os.path.join('img','kid_2.png'),
					os.path.join('img','kid_3.png'),
					os.path.join('img','kid_4.png'))
images_kid_mo = map(lambda img: pyglet.image.load(img), image_kid_frame)
kid_mo = pyglet.image.Animation.from_image_sequence(images_kid_mo, 0.1)
###resourse###

vitality = 100 #overall health gangsta on all levels
first_kit = None #take first medical_kit

#load map
map_lv1 = load(os.path.join('map','park-map1.xml'))['level1']
map_lv2 = load(os.path.join('map','park-map2.xml'))['level2']
map_lv3 = load(os.path.join('map','park-map3.xml'))['level3']
list_map = [map_lv1, map_lv2, map_lv3] #list all map in game

list_sm = [] # list all scrolling manager

#for each map create level
#create main layer, before create scrolling manager and add map and main layer
for i in range(len(list_map)):
	main_layer = MainLayer(i)
	scrolling_manager = ScrollingManager()
	scrolling_manager.add(main_layer)
	scrolling_manager.add(list_map[i])
	list_sm.append(scrolling_manager)

bg_color = ColorLayer(255, 255, 255, 255)
bg_color1 = ColorLayer(255, 255, 255, 200)
bg_color2 = ColorLayer(255, 255, 255, 170)
bg_color_final = ColorLayer(255, 255, 255, 170)

level1 = Scene(bg_color, list_sm[0], TextLayer())
level2 = Scene(bg_color1, list_sm[1], TextLayer())
level3 = Scene(bg_color2, list_sm[2], TextLayer())
final = Scene(bg_color_final, FinalLayer())

list_level = [level1, level2, level3, final]

#director.run(list_level[0])
#director.run(final)

if __name__ == '__main__':
	print "You run gangsta.py, you need run run.py"
