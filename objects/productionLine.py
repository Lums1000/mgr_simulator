import pygame as pg

from settings import *


class ProductionLine(pg.sprite.Sprite):
    def __init__(self, sim, x, y):
        self._layer = PRODUCTION_LINE_LAYER
        self.groups = sim.all_sprites, sim.production_lines
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.image_1 = self.sim.productionLineSpriteSheet.get_image_sprite_pos(0, 0, 200, 140)
        self.image_2 = self.sim.productionLineSpriteSheet.get_image_sprite_pos(1, 0, 200, 140)
        self.image_3 = self.sim.productionLineSpriteSheet.get_image_sprite_pos(2, 0, 200, 140)
        self.image_4 = self.sim.productionLineSpriteSheet.get_image_sprite_pos(3, 0, 200, 140)
        self.image_1.set_colorkey(WHITE)
        self.image_2.set_colorkey(WHITE)
        self.image_3.set_colorkey(WHITE)
        self.image_4.set_colorkey(WHITE)
        self.image = self.image_1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.t = 0
        self.dt = 1.02  # Set by observation (for bottle speed equal to production line speed)

    def update(self):
        if self.sim.production_line_run and self.sim.is_start:
            self.t += self.dt
            if self.t > 40:
                self.t = 0
            if self.t < 10:
                self.image = self.image_1
            elif self.t < 20:
                self.image = self.image_2
            elif self.t < 30:
                self.image = self.image_3
            else:
                self.image = self.image_4
