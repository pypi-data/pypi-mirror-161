from reportlab.lib.colors import HexColor
import pathlib
from os import path

DEFAULT_SPACING = 8
DEFAULT_STARTING_POSITION = 24
CIRCLE_SIZE = 4

DEFAULT_FONT = 'Helvetica'
DEFAULT_FONT_BOLD = 'Helvetica-Bold'

DEFAULT_LOGO_PATH = path.join(pathlib.Path(__file__).parent.resolve(), 'assets', 'frigel_logo.png')

WORKING_MODE_TYPES = ['standard', 'production', 'maintenance']

DEFAULT_ON_COLOR = HexColor("#39D263")
DEFAULT_OFF_COLOR = HexColor("#E9E9E9")
DEFAULT_STROKE_COLOR = HexColor("#E9E9E9")
WORKING_MODES_COLORS = (HexColor("#6bce70"), HexColor("#bedaa4"), HexColor("#4e70ab"))