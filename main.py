import math
import time
from os import path

from bottle import Bottle
from machine import *
from plcReloadData import PLCWrite, PLCRead, PLCStatus
from productionLine import ProductionLine
from sprites import *


class Simulator:
    def __init__(self):
        # initialize simulator window, etc.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        # pg.display.set_icon()
        self.clock = pg.time.Clock()
        self.font_name = pg.font.match_font(FONT_NAME)
        self.dir = ''
        self.plc_address = ''
        self.plc_rack = 0
        self.plc_slot = 1
        self.plc_port = 102  # default port: 102
        self.plc_status_thread = None
        self.plc_read_thread = None
        self.plc_write_thread = None
        self.inputs = []
        self.outputs = []
        self.io_lock = False
        self.running = False
        self.self_processing_on = False
        self.allow_keyboard = False
        self.wait_for_mouse_release = False
        self.broken_bottle_chance = BROKEN_BOTTLE_PROB
        self.last_bottle = None
        self.texts = []

        self.sim_count = 0
        self.status_thread_count = 0
        self.write_thread_count = 0
        self.read_thread_count = 0
        self.status_operation_count = 0
        self.write_operation_count = 0
        self.read_operation_count = 0
        self.time_mem = 0
        self.time = 0

    def initial(self):
        # Simulation initialization
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        # Load images
        self.background = pg.image.load(path.join(img_dir, "bg.png")).convert()
        self.machine_A = pg.image.load(path.join(img_dir, "machine_A.png")).convert()
        self.machine_B = pg.image.load(path.join(img_dir, "machine_B.png")).convert()
        self.machine_C = pg.image.load(path.join(img_dir, "machine_C.png")).convert()
        self.machine_A_top = pg.image.load(path.join(img_dir, "machine_A_top.png")).convert()
        self.machine_B_top = pg.image.load(path.join(img_dir, "machine_B_top.png")).convert()
        self.machine_C_top = pg.image.load(path.join(img_dir, "machine_C_top.png")).convert()
        self.machine_A_sensor = pg.image.load(path.join(img_dir, "machine_A_sensor.png")).convert()
        self.machine_B_sensor = pg.image.load(path.join(img_dir, "machine_B_sensor.png")).convert()
        self.machine_C_sensor = pg.image.load(path.join(img_dir, "machine_C_sensor.png")).convert()
        self.laser = pg.image.load(path.join(img_dir, "laser.png")).convert()
        self.bottle_images = []  # For loading bottle sprites with alpha channel
        for i in range(1, 5):
            self.bottle_images.append(
                pg.image.load(path.join(img_dir, 'bottle_sprite_part{}.png'.format(i))).convert_alpha())
        self.checked = pg.image.load(path.join(img_dir, 'checked.png'.format())).convert_alpha()
        # Load sprite sheets
        self.lightGreenSpriteSheet = Spritesheet(path.join(img_dir, "light_green_sprites.png"))
        self.lightOrangeSpriteSheet = Spritesheet(path.join(img_dir, "light_orange_sprites.png"))
        self.lightRedSpriteSheet = Spritesheet(path.join(img_dir, "light_red_sprites.png"))
        self.productionLineSpriteSheet = Spritesheet(path.join(img_dir, "production_line_sprites.png"))
        # Render constance texts
        self.texts.append(self.render_text("Broken bottle chance: ", 20, WHITE))
        self.texts.append(self.render_text("current chance: " + str(self.broken_bottle_chance) + "%", 20, WHITE))
        self.texts.append(self.render_text("Self processing:", 20, WHITE))
        self.texts.append(self.render_text("Allow keyboard:", 20, WHITE))
        self.texts.append(self.render_text("PLC info:", 20, WHITE))
        self.texts.append(self.render_text("PLC connected: False", 15, WHITE))
        self.texts.append(self.render_text("PLC name: unknown", 15, WHITE))
        self.texts.append(self.render_text("PLC type: unknown", 15, WHITE))
        self.texts.append(self.render_text("CPU state: unknown", 15, WHITE))
        # Preparing io area
        for i in range(22):
            self.inputs.append(False)
        self.inputs[0] = True
        for i in range(16):
            self.outputs.append(False)
        # Reading settings from .ini file
        with open(path.join(self.dir, INI_FILE), 'r') as f:
            try:
                values = f.read().split(",")
                self.plc_address = str(values[0])
                self.plc_rack = int(values[1])
                self.plc_slot = int(values[2])
                self.plc_port = int(values[3])
                self.broken_bottle_chance = int(values[4])
            except Exception as e:
                print(e)
        # Resetting counters for measurements
        self.sim_count = 0
        self.status_thread_count = 0
        self.write_thread_count = 0
        self.read_thread_count = 0
        self.status_operation_count = 0
        self.write_operation_count = 0
        self.read_operation_count = 0
        self.time_mem = 0
        self.time = 0
        # Preparing new simulation
        self.new()

    def new(self):
        # Simulation startup
        # Creating simulation object groups
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.machines = pg.sprite.Group()
        self.machines_top = pg.sprite.Group()
        self.machines_sensor = pg.sprite.Group()
        self.lasers = pg.sprite.Group()
        self.lights = pg.sprite.Group()
        self.bottles = pg.sprite.Group()
        self.production_lines = pg.sprite.Group()
        # Creating simulation objects
        machine_types = ["A", "B", "C"]
        for i in range(3):
            MachineTop(self, 250 + i * 250, 0, machine_types[i])
            Machine(self, 250 + i * 250, 135, machine_types[i])
            MachineSensor(self, 250 + i * 250, 335, machine_types[i])
        for i in range(5):
            ProductionLine(self, 0 + i * 200, 460)
        # creating first bottle
        self.last_bottle = Bottle(self, -100, 320)
        # Creating control variables
        self.production_line_run = True  # production line run (input)
        self.machine_A_ROG = [False, False, False]  # machine sensor lights red/orange/green (inputs)
        self.machine_B_ROG = [False, False, False]
        self.machine_C_ROG = [False, False, False]
        self.machine_A_top_ROG = [False, False, False]  # machine top lights red/orange/green (inputs)
        self.machine_B_top_ROG = [False, False, False]
        self.machine_C_top_ROG = [False, False, False]
        self.machine_A_LR = [False, False]  # sensors left/right (outputs)
        self.machine_B_LR = [False, False]
        self.machine_C_LR = [False, False]
        # operation start/cycle/ok/nok (input/output/output/output)
        self.machine_A_operation = [False, False, False, False]
        self.machine_B_operation = [False, False, False, False]
        self.machine_C_operation = [False, False, False, False]
        # Creating self_processing variables
        self.openA = True
        self.openB = True
        self.openC = True
        self.during_operation = False
        self.broken_bottle_to_B = False
        self.broken_bottle_to_C = False
        # Starting simulation
        self.self_processing_on = False
        self.allow_keyboard = False
        self.run()

    def run(self):
        # Creating status/read/write threads for exchanging data with PLC
        self.plc_status_thread = PLCStatus(self)
        self.plc_status_thread.start()
        self.plc_read_thread = PLCRead(self)
        self.plc_read_thread.start()
        self.plc_write_thread = PLCWrite(self)
        self.plc_write_thread.start()
        # Simulation loop
        self.running = True
        self.time_mem = time.time()
        while self.running:
            self.sim_count += 1
            self.clock.tick()
            self.events()
            self.update()
            if self.self_processing_on:
                self.self_processing()
            else:
                self.plc_connection_refresh()
            self.draw()
            if time.time() - self.time_mem > 60:
                self.running = False
        # at the end finish threads processes
        if not self.running:
            self.plc_read_thread.running = False
            self.plc_write_thread.running = False
            self.plc_status_thread.running = False
            self.plc_read_thread.join()
            self.plc_write_thread.join()
            self.plc_status_thread.join()

    def events(self):
        # Simulation loop events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                self.running = False
            # check for pressing keyboard key
            if event.type == pg.KEYDOWN:
                if self.allow_keyboard:
                    if event.key == pg.K_SPACE:
                        self.production_line_run = not self.production_line_run
                    if event.key == pg.K_a:
                        self.machine_A_operation[0] = True
                    if event.key == pg.K_b:
                        self.machine_B_operation[0] = True
                    if event.key == pg.K_c:
                        self.machine_C_operation[0] = True
            # check for releasing keyboard key
            if event.type == pg.KEYUP:
                if self.allow_keyboard:
                    if event.key == pg.K_SPACE:
                        self.production_line_run = self.production_line_run
                    if event.key == pg.K_a:
                        self.machine_A_operation[0] = False
                    if event.key == pg.K_b:
                        self.machine_B_operation[0] = False
                    if event.key == pg.K_c:
                        self.machine_C_operation[0] = False
            # check for pressing mouse button
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                x = pos[0]
                y = pos[1]
                # switching self_processing_on and allow_keyboard settings
                if 160 <= x <= 185 and not self.wait_for_mouse_release:
                    if 110 <= y <= 135:
                        self.self_processing_on = not self.self_processing_on
                        self.wait_for_mouse_release = True
                    if 150 <= y <= 175:
                        self.allow_keyboard = not self.allow_keyboard
                        self.wait_for_mouse_release = True
            # check for releasing mouse button
            if event.type == pg.MOUSEBUTTONUP:
                self.wait_for_mouse_release = False
        # continuous checking of mouse position for smoothing slider changes
        if pg.mouse.get_pressed()[0]:
            pos = pg.mouse.get_pos()
            x = pos[0]
            y = pos[1]
            # check if mouse is on proper position  of broken bottle chance setting
            if 10 <= x <= 230:
                if 45 <= y <= 65:
                    if x < 20:
                        x = 20
                    if x > 220:
                        x = 220
                    x -= 20
                    self.broken_bottle_chance = math.ceil(x / 2)
                    self.texts[1] = self.render_text("current chance: " + str(self.broken_bottle_chance) + "%", 20, WHITE)

    def update(self):
        # Simulation loop update
        self.all_sprites.update()
        # spawning next bottles in equal distances
        if self.last_bottle.rect.x >= 150:
            self.last_bottle = Bottle(self, -100, 320)

    def self_processing(self):
        # Simulation self processing loop update
        # starting production line after all tasks are complete, or when no ones in progress
        if self.during_operation:
            if not self.machine_A_operation[1] and not self.machine_B_operation[1] and not self.machine_C_operation[1]:
                self.during_operation = False
                self.production_line_run = True
        else:
            self.production_line_run = True

        # detecting task to do and machine sensor light control...
        # ...for machine A
        if self.machine_A_LR[0] and self.machine_A_LR[1]:
            self.machine_A_ROG = [False, False, True]
            if self.openA:
                self.production_line_run = False
                self.machine_A_operation[0] = True
                self.during_operation = True
                self.openA = False
        elif self.machine_A_LR[0] or self.machine_A_LR[1]:
            self.machine_A_ROG = [False, True, False]
            self.openA = True
        else:
            self.machine_A_ROG = [True, False, False]
        # ...for machine B (passing information about broken bottles on line)
        if self.machine_B_LR[0] and self.machine_B_LR[1]:
            self.machine_B_ROG = [False, False, True]
            if self.openB and not self.broken_bottle_to_B:
                self.production_line_run = False
                self.machine_B_operation[0] = True
                self.during_operation = True
                self.openB = False
        elif self.machine_B_LR[0] or self.machine_B_LR[1]:
            if self.machine_B_LR[0]:
                if self.machine_A_operation[3]:
                    self.broken_bottle_to_B = True
                else:
                    self.broken_bottle_to_B = False
            if self.machine_B_LR[1]:
                if self.broken_bottle_to_B:
                    self.broken_bottle_to_C = True
                else:
                    self.broken_bottle_to_C = False
            self.machine_B_ROG = [False, True, False]
            self.openB = True
        else:
            self.machine_B_ROG = [True, False, False]
        # ...for machine C
        if self.machine_C_LR[0] and self.machine_C_LR[1]:
            self.machine_C_ROG = [False, False, True]
            if self.openC and not self.broken_bottle_to_C:
                self.production_line_run = False
                self.machine_C_operation[0] = True
                self.during_operation = True
                self.openC = False
        elif self.machine_C_LR[0] or self.machine_C_LR[1]:
            self.machine_C_ROG = [False, True, False]
            self.openC = True
        else:
            self.machine_C_ROG = [True, False, False]

        # reset task start signal during machine cycle
        if self.machine_A_operation[1]:
            self.machine_A_operation[0] = False
        if self.machine_B_operation[1]:
            self.machine_B_operation[0] = False
        if self.machine_C_operation[1]:
            self.machine_C_operation[0] = False

        # update machine top lights state
        self.machine_A_top_ROG = [self.machine_A_operation[3], self.machine_A_operation[1], self.machine_A_operation[2]]
        self.machine_B_top_ROG = [self.machine_B_operation[3], self.machine_B_operation[1], self.machine_B_operation[2]]
        self.machine_C_top_ROG = [self.machine_C_operation[3], self.machine_C_operation[1], self.machine_C_operation[2]]

    def plc_connection_refresh(self):
        # data access control
        if not self.io_lock:
            self.io_lock = True

            # update simulation outputs
            self.outputs = [self.machine_A_LR[0], self.machine_A_LR[1],
                            self.machine_B_LR[0], self.machine_B_LR[1],
                            self.machine_C_LR[0], self.machine_C_LR[1],
                            self.machine_A_operation[1], self.machine_A_operation[2], self.machine_A_operation[3],
                            self.machine_B_operation[1], self.machine_B_operation[2], self.machine_B_operation[3],
                            self.machine_C_operation[1], self.machine_C_operation[2], self.machine_C_operation[3],
                            False]

            # update simulation inputs
            self.production_line_run = self.inputs[0]
            self.machine_A_ROG = self.inputs[1:4]
            self.machine_B_ROG = self.inputs[4:7]
            self.machine_C_ROG = self.inputs[7:10]
            self.machine_A_top_ROG = self.inputs[10:13]
            self.machine_B_top_ROG = self.inputs[13:16]
            self.machine_C_top_ROG = self.inputs[16:19]
            self.machine_A_operation[0] = self.inputs[19]
            self.machine_B_operation[0] = self.inputs[20]
            self.machine_C_operation[0] = self.inputs[21]

            self.io_lock = False

    def draw(self):
        # Simulation drawing loop
        # drawing background
        self.screen.blit(self.background, (0, 0))
        # self.all_sprites.draw(self.screen)  # not in use as the sprites update queue is specified
        # draw sprites under bottle liquid
        self.machines_sensor.draw(self.screen)
        self.production_lines.draw(self.screen)
        # draw bottle liquid
        for bottle in self.bottles:
            if not bottle.broken:
                s = pg.Surface((86, bottle.filled))
                s.set_alpha(255 * bottle.filler_transparency)
                s.fill(bottle.filler_color)
                self.screen.blit(s, (bottle.rect.x + 1, bottle.rect.y + 55 + 130 - bottle.filled))
        # draw sprites above bottle liquid
        self.bottles.draw(self.screen)
        self.machines.draw(self.screen)
        self.machines_top.draw(self.screen)
        # draw simulator settings...
        # ...for broken bottle chance
        self.screen.blit(self.texts[0], (10, 10))  # 'Broken bottle chance:'
        pg.draw.rect(self.screen, WHITE, (20, 50, 200, 1))
        pg.draw.circle(self.screen, WHITE, (20 + (self.broken_bottle_chance * 2), 50), 10)
        self.screen.blit(self.texts[1], (20, 70))  # 'current chance: <value>%'
        # ...for self processing
        self.screen.blit(self.texts[2], (10, 110))  # 'Self processing:'
        pg.draw.rect(self.screen, WHITE, (160, 110, 25, 25))
        if self.self_processing_on:
            self.screen.blit(self.checked, (160, 110))
        # ...for allowing keyboard
        self.screen.blit(self.texts[3], (10, 150))  # 'Allow keyboard:'
        pg.draw.rect(self.screen, WHITE, (160, 150, 25, 25))
        if self.allow_keyboard:
            self.screen.blit(self.checked, (160, 150))
        # PLC status update
        self.screen.blit(self.texts[4], (10, 190))  # 'PLC info:'
        self.screen.blit(self.texts[5], (20, 220))  # 'PLC connected:...'
        self.screen.blit(self.texts[6], (20, 240))  # 'PLC name:...'
        self.screen.blit(self.texts[7], (20, 260))  # 'PLC type:...'
        self.screen.blit(self.texts[8], (20, 280))  # 'CPU state:...'
        # flip the display after drawing everything
        pg.display.flip()

    # def draw_text(self, text, size, color, x, y):
    #     # Additional helping function for drawing text
    #     font = pg.font.Font(self.font_name, size)
    #     text_surface = font.render(text, True, color)
    #     self.screen.blit(text_surface, (x, y))

    def render_text(self, text, size, color):
        # Additional helping function for rendering text
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        return text_surface


# Main
if __name__ == '__main__':
    g = Simulator()
    g.initial()

    print('sim_count: ' + str(g.sim_count))
    print('status_thread_count: ' + str(g.status_thread_count))
    print('status_operation_count: ' + str(g.status_operation_count))
    print('write_thread_count: ' + str(g.write_thread_count))
    print('write_operation_count: ' + str(g.write_operation_count))
    print('read_thread_count: ' + str(g.read_thread_count))
    print('read_operation_count: ' + str(g.read_operation_count))
    pg.quit()
