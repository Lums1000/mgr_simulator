import tkinter as tk
from tkinter import *


class Window(Frame):
    def __init__(self, root=None, sim=None):
        Frame.__init__(self, root)
        self.root = root
        self.sim = sim
        # set window title
        self.root.wm_title("Tkinter window")
        self.root.geometry("600x400")

        self.ip = tk.StringVar(self.root, 'test')
        self.rack = tk.StringVar(self.root, 'test')
        self.slot = tk.StringVar(self.root, 'test')
        self.port = tk.StringVar(self.root, 'test')
        self.ip_label = tk.Label(root, text='IP address', font=('calibre', 10, 'bold'))
        self.rack_label = tk.Label(root, text='Rack', font=('calibre', 10, 'bold'))
        self.slot_label = tk.Label(root, text='Slot', font=('calibre', 10, 'bold'))
        self.port_label = tk.Label(root, text='Port', font=('calibre', 10, 'bold'))

        # creating a entry for input
        # name using widget Entry
        self.ip_entry = tk.Entry(root, textvariable=self.ip, font=('calibre', 10, 'normal'))
        self.rack_entry = tk.Entry(root, textvariable=self.rack, font=('calibre', 10, 'normal'))
        self.slot_entry = tk.Entry(root, textvariable=self.slot, font=('calibre', 10, 'normal'))
        self.port_entry = tk.Entry(root, textvariable=self.port, font=('calibre', 10, 'normal'))

        self.sub_btn = tk.Button(root, text='Confirm', command=self.submit)

        self.ip_label.grid(row=0, column=0)
        self.rack_label.grid(row=0, column=1)
        self.slot_label.grid(row=0, column=2)
        self.port_label.grid(row=0, column=3)
        self.ip_entry.grid(row=1, column=0)
        self.rack_entry.grid(row=1, column=1)
        self.slot_entry.grid(row=1, column=2)
        self.port_entry.grid(row=1, column=3)
        self.sub_btn.grid(row=2, column=3)

        # show window
        self.root.mainloop()

    def submit(self):
        self.sim.ip = self.ip.get()
        self.sim.rack = self.rack.get()
        self.sim.slot = self.slot.get()
        self.sim.port = self.port.get()
        self.root.quit()
