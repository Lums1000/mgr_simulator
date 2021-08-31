import pygame as pg

from settings import *


class Light(pg.sprite.Sprite):
    def __init__(self, sim, x, y, light_type):
        self._layer = MACHINE_SENSOR_LAYER
        self.groups = sim.all_sprites, sim.machines_sensor, sim.lights
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.type = light_type
        if self.type == "R":
            self.image_off = self.sim.lightRedSpriteSheet.get_image_sprite_pos(0, 0, 15, 10)
            self.image_on = self.sim.lightRedSpriteSheet.get_image_sprite_pos(1, 0, 15, 10)
        elif self.type == "O":
            self.image_off = self.sim.lightOrangeSpriteSheet.get_image_sprite_pos(0, 0, 15, 10)
            self.image_on = self.sim.lightOrangeSpriteSheet.get_image_sprite_pos(1, 0, 15, 10)
        elif self.type == "G":
            self.image_off = self.sim.lightGreenSpriteSheet.get_image_sprite_pos(0, 0, 15, 10)
            self.image_on = self.sim.lightGreenSpriteSheet.get_image_sprite_pos(1, 0, 15, 10)
        self.is_on = False
        self.image = self.image_off
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.is_on:
            self.image = self.image_on
        else:
            self.image = self.image_off


class Light2(pg.sprite.Sprite):
    def __init__(self, sim, x, y, light_type):
        self._layer = MACHINE_TOP_LAYER
        self.groups = sim.all_sprites, sim.machines_top, sim.lights
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.type = light_type
        if self.type == "R":
            self.image_off = self.sim.lightRedSpriteSheet.get_image_sprite_pos(0, 0, 15, 10)
            self.image_on = self.sim.lightRedSpriteSheet.get_image_sprite_pos(1, 0, 15, 10)
        elif self.type == "O":
            self.image_off = self.sim.lightOrangeSpriteSheet.get_image_sprite_pos(0, 0, 15, 10)
            self.image_on = self.sim.lightOrangeSpriteSheet.get_image_sprite_pos(1, 0, 15, 10)
        elif self.type == "G":
            self.image_off = self.sim.lightGreenSpriteSheet.get_image_sprite_pos(0, 0, 15, 10)
            self.image_on = self.sim.lightGreenSpriteSheet.get_image_sprite_pos(1, 0, 15, 10)
        self.is_on = False
        self.image = self.image_off
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.is_on:
            self.image = self.image_on
        else:
            self.image = self.image_off
