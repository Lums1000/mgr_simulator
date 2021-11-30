import pygame as pg

from objects.laser import Laser
from objects.light import Light, Light2
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
        else:
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
        else:
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
            self.end_pos = 165
            self.tool_duration = 250
        elif self.type == "B":
            self.image = images[1]
            self.end_pos = 140
            self.tool_duration = 1500
        else:
            self.image = images[2]
            self.end_pos = 170
            self.tool_duration = 500
        self.start_pos = 135
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.allow_pos = [self.rect.x + 54, self.rect.x + 58]
        self.tool_started = None
        self.current_time = None
        self.current_bottle = None
        self.current_bottle_pos = None
        self.lock_filler_update = False
        # Creating self processing variables
        self.self_processing_on = False
        self.self_processing_mem = False
        self.sp_during_cycle = False
        self.sp_cycle_state = 1
        self.sp_cycle_ok = False
        self.sp_cycle_nok = False
        # Creating edge detecting variables
        self.last_ack_state = False
        self.last_tool_on_state = False
        self.last_tool_off_state = False
        self.last_sp_start_state = False
        # Creating operation variable...
        # ...inputs
        self.operation_go_down = False
        self.operation_go_up = False
        self.operation_tool_on = False
        self.operation_tool_off = False
        self.operation_ack = False
        self.operation_sp_start = False
        # ...outputs
        self.operation_start_pos = False
        self.operation_end_pos = False
        self.operation_tool_work = False
        self.operation_tool_ready = False
        self.operation_error = False

    def update(self):
        # switching self_processing_on option
        if self.sim.self_processing_on or self.sim.manual_mode_on:
            self.self_processing_on = True
        else:
            self.self_processing_on = self.self_processing_mem

        # updating inputs
        if self.type == "A":
            if not self.self_processing_on:
                self.operation_go_down = self.sim.machine_A_operation_in[0]
                self.operation_go_up = self.sim.machine_A_operation_in[1]
                self.operation_tool_on = self.sim.machine_A_operation_in[2]
                self.operation_tool_off = self.sim.machine_A_operation_in[3]
            self.operation_ack = self.sim.machine_A_operation_in[4]
            self.operation_sp_start = self.sim.machine_A_operation_in[5]
        elif self.type == "B":
            if not self.self_processing_on:
                self.operation_go_down = self.sim.machine_B_operation_in[0]
                self.operation_go_up = self.sim.machine_B_operation_in[1]
                self.operation_tool_on = self.sim.machine_B_operation_in[2]
                self.operation_tool_off = self.sim.machine_B_operation_in[3]
            self.operation_ack = self.sim.machine_B_operation_in[4]
            self.operation_sp_start = self.sim.machine_B_operation_in[5]
        else:
            if not self.self_processing_on:
                self.operation_go_down = self.sim.machine_C_operation_in[0]
                self.operation_go_up = self.sim.machine_C_operation_in[1]
                self.operation_tool_on = self.sim.machine_C_operation_in[2]
                self.operation_tool_off = self.sim.machine_C_operation_in[3]
            self.operation_ack = self.sim.machine_C_operation_in[4]
            self.operation_sp_start = self.sim.machine_C_operation_in[5]

        # self processing, if enabled
        if self.self_processing_on:
            if (self.operation_sp_start and not self.last_sp_start_state) or self.sp_during_cycle:
                if not self.sp_during_cycle:
                    self.sp_during_cycle = True
                self.self_processing()

        # processing fragment
        if self.sim.is_start and not self.operation_error:
            self.current_time = pg.time.get_ticks()
            # process
            if self.operation_go_down and self.rect.y < self.end_pos:
                self.rect.y += 1
            if self.operation_go_up and self.rect.y > self.start_pos:
                self.rect.y -= 1
            if self.rect.y >= self.end_pos:
                self.operation_end_pos = True
            else:
                self.operation_end_pos = False
            if self.rect.y <= self.start_pos:
                self.operation_start_pos = True
            else:
                self.operation_start_pos = False
            if self.operation_tool_on and not self.last_tool_on_state:
                self.operation_tool_work = True
                self.tool_started = self.current_time
                if self.operation_end_pos:
                    for bottle in self.sim.bottles:
                        if self.allow_pos[0] <= bottle.rect.left <= self.allow_pos[1]:
                            self.current_bottle = bottle
                            self.current_bottle_pos = bottle.rect.x
                            if self.type == "B":
                                self.lock_filler_update = False
                                if self.current_bottle.filler_name == "" and self.sim.filler_index < 3:
                                    self.current_bottle.filler_name = self.sim.fillers[self.sim.filler_index].name
                                    self.current_bottle.filler_color = self.sim.filler_color
                                    self.current_bottle.filler_transparency = self.sim.filler_transparency
                                elif self.current_bottle.filler_name != "" and self.sim.filler_index < 3:
                                    if self.current_bottle.filler_name != self.sim.fillers[self.sim.filler_index].name:
                                        self.operation_error = True
                                else:
                                    self.operation_error = True
            if self.operation_tool_off and not self.last_tool_off_state:
                self.operation_tool_ready = False
                self.operation_tool_work = False
            if self.operation_tool_work:
                if self.current_bottle is not None:
                    if self.current_bottle.rect.x == self.current_bottle_pos:
                        if self.type == "A":
                            self.operation_a()
                        elif self.type == "B":
                            self.operation_b()
                        else:
                            self.operation_c()
                    else:
                        if self.allow_pos[0] <= self.current_bottle.rect.x <= self.allow_pos[1]:
                            self.current_bottle_pos = self.current_bottle.rect.x
                        else:
                            self.operation_error = True
                            self.current_bottle = None
                            self.current_bottle_pos = None
            # raise error
            if self.operation_go_down and self.operation_go_up:
                self.operation_error = True
            if self.operation_tool_on and self.operation_tool_off:
                self.operation_error = True
            if (self.operation_tool_on or self.operation_tool_work) and (self.operation_go_down or self.operation_go_up):
                self.operation_error = True
            if self.operation_error:
                self.current_bottle = None
                self.current_bottle_pos = None
                self.operation_tool_work = False
                self.operation_tool_ready = False
        else:
            # acknowledge error (only raising edge)
            if self.operation_ack and not self.last_ack_state:
                self.operation_error = False

        # remembering current states for next loop (for signal edge detection)
        self.last_ack_state = self.operation_ack
        self.last_tool_on_state = self.operation_tool_on
        self.last_tool_off_state = self.operation_tool_off
        self.last_sp_start_state = self.operation_sp_start

        # updating outputs
        if self.type == "A":
            self.sim.machine_A_operation_out[0] = self.operation_start_pos
            self.sim.machine_A_operation_out[1] = self.operation_end_pos
            self.sim.machine_A_operation_out[2] = self.operation_tool_work
            self.sim.machine_A_operation_out[3] = self.operation_tool_ready
            self.sim.machine_A_operation_out[4] = self.operation_error
        elif self.type == "B":
            self.sim.machine_B_operation_out[0] = self.operation_start_pos
            self.sim.machine_B_operation_out[1] = self.operation_end_pos
            self.sim.machine_B_operation_out[2] = self.operation_tool_work
            self.sim.machine_B_operation_out[3] = self.operation_tool_ready
            self.sim.machine_B_operation_out[4] = self.operation_error
        else:
            self.sim.machine_C_operation_out[0] = self.operation_start_pos
            self.sim.machine_C_operation_out[1] = self.operation_end_pos
            self.sim.machine_C_operation_out[2] = self.operation_tool_work
            self.sim.machine_C_operation_out[3] = self.operation_tool_ready
            self.sim.machine_C_operation_out[4] = self.operation_error

    def operation_a(self):
        if self.current_time - self.tool_started >= self.tool_duration:
            if not self.current_bottle.broken:
                self.operation_tool_ready = True
        if self.current_bottle.closed:
            self.operation_error = True

    def operation_b(self):
        if self.current_bottle.filled >= self.current_bottle.overfilled or self.current_bottle.closed:
            self.operation_error = True
        else:
            if not self.current_bottle.broken and not self.operation_error:
                if self.sim.fps > 0:
                    progress = (self.current_bottle.fill_max / self.sim.fps * (self.tool_duration / 1000))
                else:
                    progress = (self.current_bottle.fill_max / 800 * (self.tool_duration / 1000))
                if self.current_bottle.filled < self.current_bottle.overfilled:
                    self.current_bottle.filled += progress
            if self.current_bottle.filled >= self.current_bottle.fill_max:
                self.operation_tool_ready = True
                if not self.lock_filler_update:
                    self.lock_filler_update = True
                    for filler in self.sim.fillers:
                        if filler.name == self.current_bottle.filler_name:
                            if not filler.is_inf:
                                if filler.amount > 0:
                                    filler.amount -= 1
                    self.sim.filler_update = True

    def operation_c(self):
        if self.current_time - self.tool_started >= self.tool_duration and not self.operation_tool_ready:
            if self.current_bottle.closed:
                self.operation_error = True
            else:
                self.operation_tool_ready = True
                self.current_bottle.closed = True
                if self.current_bottle.broken:
                    self.current_bottle.image = self.current_bottle.image_4
                else:
                    self.current_bottle.image = self.current_bottle.image_3

    def self_processing(self):
        if self.sim.self_processing_on and not self.sim.manual_mode_on:
            if self.operation_error:
                self.operation_ack = True;
            else:
                self.operation_ack = False;
        if self.sp_cycle_state == 1:
            self.operation_go_down = True
            if self.operation_end_pos:
                self.operation_go_down = False
                self.operation_tool_on = True
                self.sp_cycle_state = 2
        elif self.sp_cycle_state == 2:
            # if tool ready
            if self.operation_tool_ready:
                self.operation_tool_on = False
                self.operation_tool_off = True
                self.sp_cycle_state = 3
            # if tool timeout
            if self.current_time - self.tool_started >= self.tool_duration * 1.5:
                self.operation_tool_on = False
                self.operation_tool_off = True
                self.sp_cycle_state = 3
        elif self.sp_cycle_state == 3:
            if not self.operation_tool_work:
                self.operation_tool_off = False
                self.operation_go_up = True
            if self.operation_start_pos:
                self.operation_go_up = False
                self.sp_during_cycle = False
                self.sp_cycle_state = 1


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
        else:
            self.image = images[2]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Creating laser sensor objects
        self.laser1 = Laser(self.sim, x + 56, y + 98)
        self.laser2 = Laser(self.sim, x + 141, y + 98)
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
        else:
            self.lightR.is_on = self.sim.machine_C_ROG[0]
            self.lightO.is_on = self.sim.machine_C_ROG[1]
            self.lightG.is_on = self.sim.machine_C_ROG[2]
            self.sim.machine_C_LR[0] = self.laser1_high
            self.sim.machine_C_LR[1] = self.laser2_high
