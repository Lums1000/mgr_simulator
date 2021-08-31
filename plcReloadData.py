import ctypes
import time
from threading import Thread

import snap7

from settings import WHITE


class PLCStatus(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self.name = 'PLCStatusThread'
        self.running = True
        self.plc = snap7.client.Client()
        self.connected = False
        self.cpu_info = ''
        self.cpu_state = ''
        self.sim = sim

    def run(self):
        while self.running:
            self.sim.status_thread_count += 1
            if not self.connected:
                try:
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                    if self.connected:
                        self.cpu_info = self.plc.get_cpu_info()
                        self.sim.texts[5] = self.sim.render_text("PLC connected: " + str(self.connected), 15, WHITE)
                        self.sim.texts[6] = self.sim.render_text("PLC name: " + self.cpu_info.ModuleName.decode(), 15, WHITE)
                        self.sim.texts[7] = self.sim.render_text("PLC type: " + self.cpu_info.ModuleTypeName.decode(), 15, WHITE)
                except Exception as e:
                    print(e)
            else:
                try:
                    # read status form PLC
                    self.sim.status_operation_count += 1
                    self.cpu_state = self.plc.get_cpu_state()
                    self.sim.texts[8] = self.sim.render_text("CPU state: " + str(self.cpu_state), 15, WHITE)
                except Exception as e:
                    print(e)
                time.sleep(1)
        if not self.running and self.connected:
            self.plc.disconnect()


class PLCWrite(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self.name = 'PLCWriteThread'
        self.running = True
        self.plc = snap7.client.Client()
        self.connected = False
        self.data = ''
        self.sim = sim
        self.result = 1

    def run(self):
        while self.running:
            self.sim.write_thread_count += 1
            if not self.connected:
                try:
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                except Exception as e:
                    print(e)
            else:
                if not self.sim.io_lock:
                    self.sim.io_lock = True
                    self.data = self.sim.outputs
                    self.sim.io_lock = False
                    outputs_bin = ''
                    for i in range(16):
                        if self.data[i]:
                            outputs_bin += '1'
                        else:
                            outputs_bin += '0'
                    outputs_bytes = int(outputs_bin[::-1], 2).to_bytes((len(outputs_bin) + 7) // 8, byteorder='little')
                    try:
                        # write to PLC
                        self.sim.write_operation_count += 1
                        self.result = self.plc.mb_write(3, 2, outputs_bytes)
                    except Exception as e:
                        print(e)
        if not self.running and self.connected:
            self.plc.disconnect()


class PLCRead(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self.name = 'PLCReadThread'
        self.running = True
        self.plc = snap7.client.Client()
        self.connected = False
        self.data = ''
        self.data_to_update = False
        self.sim = sim
        self.result = 1

    def run(self):
        while self.running:
            self.sim.read_thread_count += 1
            if not self.connected:
                try:
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                except Exception as e:
                    print(e)
            else:
                if not self.data_to_update:
                    try:
                        # read form PLC
                        # self.data = ctypes.c_buffer(3)  # buffer for async task
                        # self.result = self.plc.as_mb_read(0, 3, self.data)
                        self.sim.read_operation_count += 1
                        self.data = self.plc.mb_read(0, 3)
                        if self.result:
                            self.data = bin(int.from_bytes(self.data, byteorder='little'))
                            self.data = self.data[::-1]
                            while self.data.__len__() < 22:
                                self.data += "0"
                            self.data_to_update = True
                    except Exception as e:
                        print(e)
                if not self.sim.io_lock and self.data_to_update:
                    self.sim.io_lock = True
                    for i in range(22):
                        if self.data[i] == '1':
                            self.sim.inputs[i] = True
                        else:
                            self.sim.inputs[i] = False
                    self.data_to_update = False
                    self.sim.io_lock = False
        if not self.running and self.connected:
            self.plc.disconnect()
