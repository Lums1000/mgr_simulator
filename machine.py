import pygame as pg

from laser import Laser
from light import Light, Light2
from settings import *


class MachineTop(pg.sprite.Sprite):
    def __init__(self, sim, x, y, machine_type):
        self._layer = MACHINE_TOP_LAYER
        self.groups = sim.all_sprites, sim.machines_top
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.type = machine_type
        images = [self.sim.machine_A_top, self.sim.machine_B_top, self.sim.machine_C_top]
        images[0].set_colorkey(WHITE)
        images[1].set_colorkey(WHITE)
        images[2].set_colorkey(WHITE)
        if self.type == "A":
            self.image = images[0]
        elif self.type == "B":
            self.image = images[1]
        elif self.type == "C":
            self.image = images[2]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Creating lights objects
        self.lightR = Light2(self.sim, x + 150, y + 143, "R")
        self.lightO = Light2(self.sim, x + 35, y + 155, "O")
        self.lightG = Light2(self.sim, x + 150, y + 155, "G")

    def update(self):
        # get and set simulation control variables
        if self.type == "A":
            self.lightR.is_on = self.sim.machine_A_top_ROG[0]
            self.lightO.is_on = self.sim.machine_A_top_ROG[1]
            self.lightG.is_on = self.sim.machine_A_top_ROG[2]
        elif self.type == "B":
            self.lightR.is_on = self.sim.machine_B_top_ROG[0]
            self.lightO.is_on = self.sim.machine_B_top_ROG[1]
            self.lightG.is_on = self.sim.machine_B_top_ROG[2]
        elif self.type == "C":
            self.lightR.is_on = self.sim.machine_C_top_ROG[0]
            self.lightO.is_on = self.sim.machine_C_top_ROG[1]
            self.lightG.is_on = self.sim.machine_C_top_ROG[2]


class Machine(pg.sprite.Sprite):
    def __init__(self, sim, x, y, machine_type):
        self._layer = MACHINE_LAYER
        self.groups = sim.all_sprites, sim.machines
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.type = machine_type
        images = [self.sim.machine_A, self.sim.machine_B, self.sim.machine_C]
        images[0].set_colorkey(WHITE)
        images[1].set_colorkey(WHITE)
        images[2].set_colorkey(WHITE)
        if self.type == "A":
            self.image = images[0]
        elif self.type == "B":
            self.image = images[1]
        elif self.type == "C":
            self.image = images[2]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Creating operation variables
        self.operation_cycle = False
        self.operation_ok = False
        self.operation_nok = False
        self.operation_time = 0
        self.operation_duration = 1000
        self.operation_bottle = None
        self.operation_bottle_pos = 0
        self.operation_set_mem = False
        self.state1 = False
        self.state2 = False
        self.state3 = False

    def update(self):
        if self.type == "A":
            if self.sim.machine_A_operation[0]:
                self.operation_cycle = True
        elif self.type == "B":
            if self.sim.machine_B_operation[0]:
                self.operation_cycle = True
        elif self.type == "C":
            if self.sim.machine_C_operation[0]:
                self.operation_cycle = True
        if self.operation_cycle:
            if not self.operation_set_mem:
                if self.type == "A":
                    for bottle in self.sim.bottles:
                        if 303 <= bottle.rect.x <= 314:
                            self.operation_bottle = bottle
                            self.operation_bottle_pos = bottle.rect.x
                elif self.type == "B":
                    for bottle in self.sim.bottles:
                        if 553 <= bottle.rect.x <= 564:
                            self.operation_bottle = bottle
                            self.operation_bottle_pos = bottle.rect.x
                elif self.type == "C":
                    for bottle in self.sim.bottles:
                        if 803 <= bottle.rect.x <= 814:
                            self.operation_bottle = bottle
                            self.operation_bottle_pos = bottle.rect.x
                self.state1 = True
                self.operation_ok = False
                self.operation_nok = False
                self.operation_set_mem = True
            if self.type == "A":
                self.operation_A()
                self.sim.machine_A_operation[1] = self.operation_cycle
                self.sim.machine_A_operation[2] = self.operation_ok
                self.sim.machine_A_operation[3] = self.operation_nok
            elif self.type == "B":
                self.operation_B()
                self.sim.machine_B_operation[1] = self.operation_cycle
                self.sim.machine_B_operation[2] = self.operation_ok
                self.sim.machine_B_operation[3] = self.operation_nok
            elif self.type == "C":
                self.operation_C()
                self.sim.machine_C_operation[1] = self.operation_cycle
                self.sim.machine_C_operation[2] = self.operation_ok
                self.sim.machine_C_operation[3] = self.operation_nok

    def operation_A(self):
        if self.state1:
            self.rect.y += 1  # speed of running tool down
            if self.rect.y >= 165:
                self.state1 = False
                self.state2 = True
                self.operation_time = pg.time.get_ticks()
        if self.state2:
            if pg.time.get_ticks() - self.operation_time >= self.operation_duration:
                if self.operation_bottle is not None:
                    if self.operation_bottle.broken:
                        self.operation_ok = False
                        self.operation_nok = True
                    elif self.operation_bottle_pos != self.operation_bottle.rect.x:
                        self.operation_ok = False
                        self.operation_nok = True
                    else:
                        self.operation_ok = True
                        self.operation_nok = False
                else:
                    self.operation_ok = False
                    self.operation_nok = True
                self.state2 = False
                self.state3 = True
        if self.state3:
            self.rect.y -= 1  # speed of running tool up
            if self.rect.y <= 135:
                self.state3 = False
                self.operation_set_mem = False
                self.operation_cycle = False
                self.operation_bottle = None

    def operation_B(self):
        if self.state1:
            self.rect.y += 1  # speed of running tool down
            if self.rect.y >= 140:
                self.state1 = False
                self.state2 = True
                self.operation_time = pg.time.get_ticks()
        if self.state2:
            if self.operation_bottle is None:
                self.operation_ok = False
                self.operation_nok = True
                self.state2 = False
                self.state3 = True
            else:
                if self.operation_bottle_pos == self.operation_bottle.rect.x:
                    if not self.operation_bottle.broken:
                        # preventing of overfilling bottle
                        if self.operation_bottle.filled < self.operation_bottle.fill_max:
                            self.operation_bottle.filled += 2
                if pg.time.get_ticks() - self.operation_time >= self.operation_duration:
                    if self.operation_bottle_pos == self.operation_bottle.rect.x:
                        self.operation_ok = True
                        self.operation_nok = False
                    else:
                        self.operation_ok = False
                        self.operation_nok = True
                    self.state2 = False
                    self.state3 = True
        if self.state3:
            self.rect.y -= 1  # speed of running tool up
            if self.rect.y <= 135:
                self.state3 = False
                self.operation_set_mem = False
                self.operation_cycle = False
                self.operation_bottle = None

    def operation_C(self):
        if self.state1:
            self.rect.y += 1  # speed of running tool down
            if self.rect.y >= 170:
                self.state1 = False
                self.state2 = True
                self.operation_time = pg.time.get_ticks()
        if self.state2:
            if self.operation_bottle is None:
                self.operation_ok = False
                self.operation_nok = True
                self.state2 = False
                self.state3 = True
            elif pg.time.get_ticks() - self.operation_time >= self.operation_duration:
                if self.operation_bottle_pos == self.operation_bottle.rect.x:
                    self.operation_ok = True
                    self.operation_nok = False
                else:
                    self.operation_ok = False
                    self.operation_nok = True
                if self.operation_ok:
                    if self.operation_bottle.broken:
                        self.operation_bottle.image = self.operation_bottle.image_4
                    else:
                        self.operation_bottle.image = self.operation_bottle.image_3
                self.state2 = False
                self.state3 = True
        if self.state3:
            self.rect.y -= 1  # speed of running tool up
            if self.rect.y <= 135:
                self.state3 = False
                self.operation_set_mem = False
                self.operation_cycle = False
                self.operation_bottle = None


class MachineSensor(pg.sprite.Sprite):
    def __init__(self, sim, x, y, machine_type):
        self._layer = MACHINE_SENSOR_LAYER
        self.groups = sim.all_sprites, sim.machines_sensor
        pg.sprite.Sprite.__init__(self, self.groups)
        self.sim = sim
        self.type = machine_type
        images = [self.sim.machine_A_sensor, self.sim.machine_B_sensor, self.sim.machine_C_sensor]
        images[0].set_colorkey(WHITE)
        images[1].set_colorkey(WHITE)
        images[2].set_colorkey(WHITE)
        if self.type == "A":
            self.image = images[0]
        elif self.type == "B":
            self.image = images[1]
        elif self.type == "C":
            self.image = images[2]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Creating laser sensor objects
        self.laser1 = Laser(self.sim, x + 57, y + 98)
        self.laser2 = Laser(self.sim, x + 142, y + 98)
        self.laser1_high = False
        self.laser2_high = False
        # Creating lights objects
        self.lightR = Light(self.sim, x + 26, y + 14, "R")
        self.lightO = Light(self.sim, x + 26, y + 25, "O")
        self.lightG = Light(self.sim, x + 26, y + 36, "G")

    def update(self):
        # detect collision of bottles with lasers
        hits = pg.sprite.spritecollide(self.laser1, self.sim.bottles, False)
        if hits:
            self.laser1_high = True
        else:
            self.laser1_high = False
        hits = pg.sprite.spritecollide(self.laser2, self.sim.bottles, False)
        if hits:
            self.laser2_high = True
        else:
            self.laser2_high = False
        # get and set simulation control variables
        if self.type == "A":
            self.lightR.is_on = self.sim.machine_A_ROG[0]
            self.lightO.is_on = self.sim.machine_A_ROG[1]
            self.lightG.is_on = self.sim.machine_A_ROG[2]
            self.sim.machine_A_LR[0] = self.laser1_high
            self.sim.machine_A_LR[1] = self.laser2_high
        elif self.type == "B":
            self.lightR.is_on = self.sim.machine_B_ROG[0]
            self.lightO.is_on = self.sim.machine_B_ROG[1]
            self.lightG.is_on = self.sim.machine_B_ROG[2]
            self.sim.machine_B_LR[0] = self.laser1_high
            self.sim.machine_B_LR[1] = self.laser2_high
        elif self.type == "C":
            self.lightR.is_on = self.sim.machine_C_ROG[0]
            self.lightO.is_on = self.sim.machine_C_ROG[1]
            self.lightG.is_on = self.sim.machine_C_ROG[2]
            self.sim.machine_C_LR[0] = self.laser1_high
            self.sim.machine_C_LR[1] = self.laser2_high
