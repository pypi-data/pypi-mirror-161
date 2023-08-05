import os

VERSION = "dev.999"
PLUGIN_DIR = os.path.dirname(__file__)
try:
    with open(os.path.join(PLUGIN_DIR, "VERSION")) as version_file:
        VERSION = version_file.read().strip()
except BaseException:
    pass

RIGHT_COLUMN_WIDTH = 100
RIGHT_COLUMN_WIDTH_PLUS = 105
