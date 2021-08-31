from random import randrange

import pygame as pg

from settings import *


class Bottle(pg.sprite.Sprite):
    def __init__(self, sim, x, y):
        self._layer = BOTTLE_LAYER
        self.groups = sim.all_sprites, sim.bottles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.image_1 = self.sim.bottle_images[0]
        self.image_2 = self.sim.bottle_images[1]
        self.image_3 = self.sim.bottle_images[2]
        self.image_4 = self.sim.bottle_images[3]
        # Draw a bottle condition (broken or not)
        self.broken = randrange(100) < self.sim.broken_bottle_chance
        if self.broken:
            self.image = self.image_2
        else:
            self.image = self.image_1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Bottle filler variables
        self.filled = 0
        self.closed = False
        self.fill_max = 130  # max 130
        self.filler_color = FILLER_COLOR
        self.filler_transparency = FILLER_TRANSPARENCY

    def update(self):
        # moving bottle with production line
        if self.sim.production_line_run:
            self.rect.x += 1
        # destroying objects out of screen
        if self.rect.left > WIDTH:
            self.kill()
