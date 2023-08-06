import xlwt
from openpyxl.styles import PatternFill
from openpyxl.styles.colors import COLOR_INDEX
from RiceXL.RiceUtils import get_color_rgb, get_color_rgb_by_index

FILL_TYPE = (
    'none', #0
    'solid', #1
    'mediumGray', #2
    'darkGray', #3
    'lightGray', #4
    'darkHorizontal', #5
    'darkVertical', #6
    'darkDown', #7
    'darkUp', #8
    'darkGrid', #9
    'darkTrellis', #10
    'lightHorizontal', #11
    'lightVertical', #12
    'lightDown', #13
    'lightUp', #14
    'lightGrid', #15
    'lightTrellis', #16
    'gray125', #17
    'gray0625' #18
)

class RicePattern():
    _type = None
    _start_color = None
    _end_color = None

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, type):
        self._type = type
        self.pattern_xls.pattern = FILL_TYPE.index(self._type)
        self.pattern_xlsx.fill_type = None if self._type == 'none' else self._type
    
    @property
    def start_color(self):
        return self._start_color

    @start_color.setter
    def start_color(self, color):
        self._start_color = color
        self.pattern_xls.pattern_fore_colour = COLOR_INDEX.index(color)
        self.pattern_xlsx.start_color = color
    
    @property
    def end_color(self):
        return self._end_color
    
    @end_color.setter
    def end_color(self, color):
        self._end_color = color
        self.pattern_xls.pattern_back_colour = COLOR_INDEX.index(color)
        self.pattern_xlsx.end_color = color
    
    def init_xls(self, pattern):
        rice_pattern = RicePattern()
        rice_pattern.type = FILL_TYPE[pattern.pattern]
        rice_pattern.start_color = get_color_rgb_by_index(pattern.pattern_fore_colour)
        rice_pattern.end_color = get_color_rgb_by_index(pattern.pattern_back_colour)
        return rice_pattern
    
    def init_xlsx(self, pattern):
        rice_pattern = RicePattern()
        rice_pattern.type = pattern.fill_type if pattern.fill_type is not None else 'none'
        rice_pattern.start_color = get_color_rgb(pattern.start_color)
        rice_pattern.end_color = get_color_rgb(pattern.end_color)
        return rice_pattern

    def __init__(self):
        self.pattern_xls = xlwt.Pattern()
        self.pattern_xlsx = PatternFill()