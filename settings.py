# Options/settings
# Window settings
TITLE = "Filling bottles station"
INI_FILE = "simulator.ini"
WIDTH = 1000
HEIGHT = 600

# Simulation settings
BROKEN_BOTTLE_PROB = 10  # from 0 to 100 (%) ALERT! could be overwrite during initial from .ini value
FILLER_COLOR = (219, 248, 255)  # RGB form 0 to 255
FILLER_TRANSPARENCY = 0.6  # from 0 to 1
MIN_SPACE = 10
MAX_SPACE = 12
FPS = 80
MANUAL_MODE_FPS = 60

# Simulation layers properties
MACHINE_SENSOR_LAYER = 0
PRODUCTION_LINE_LAYER = 1
BOTTLE_LAYER = 2
MACHINE_LAYER = 3
MACHINE_TOP_LAYER = 4

# Defined colors
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (76, 74, 72)

# Defined fonts
FONT_NAME = 'arial'
