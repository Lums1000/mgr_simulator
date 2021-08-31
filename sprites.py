import pygame as pg


class Spritesheet:
    def __init__(self, mainFilename):
        self.spritesheet = pg.image.load(mainFilename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image

    def get_image_sprite_pos(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x * width, y * height, width, height))
        return image
