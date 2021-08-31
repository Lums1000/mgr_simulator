import pygame as pg

from settings import *


class Laser(pg.sprite.Sprite):
    def __init__(self, sim, x, y):
        self._layer = PRODUCTION_LINE_LAYER
        self.groups = sim.all_sprites, sim.lasers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.image = self.sim.laser
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
