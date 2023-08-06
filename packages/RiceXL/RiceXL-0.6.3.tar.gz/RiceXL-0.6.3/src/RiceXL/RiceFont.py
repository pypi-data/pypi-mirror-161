import xlwt
from openpyxl.styles import Font
from openpyxl.styles.colors import COLOR_INDEX
from RiceXL.RiceUtils import get_color_rgb

class RiceFont():
    UNDERLINE_DOUBLE = 'double'
    UNDERLINE_DOUBLE_ACCOUNTING = 'doubleAccounting'
    UNDERLINE_SINGLE = 'single'
    UNDERLINE_SINGLE_ACCOUNTING = 'singleAccounting'

    _name = None
    _color_index = None
    _color = None
    _size = None
    _bold = None
    _italic = None
    _underline = None
    _strike = None

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
        self.font_xls.name = self._name
        self.font_xlsx.name = self._name

    @property
    def color_index(self):
        return self._color_index
    
    @color_index.setter
    def color_index(self, color_index):
        self._color_index = color_index
        self._color = COLOR_INDEX[self._color_index]
        self.font_xls.colour_index = self._color_index
        self.font_xlsx.color = self._color

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color
        self._color_index = COLOR_INDEX.index(self._color)
        self.font_xls.colour_index = self._color_index
        self.font_xlsx.color = self._color
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, size):
        self._size = size
        self.font_xls.height = 20 * self._size
        self.font_xlsx.size = self._size

    @property
    def bold(self):
        return self._bold
    
    @bold.setter
    def bold(self, bold):
        self._bold = bold
        self.font_xls.bold = self._bold
        self.font_xlsx.bold = self._bold
    
    @property
    def italic(self):
        return self._italic
    
    @italic.setter
    def italic(self, italic):
        self._italic = italic
        self.font_xls.italic = self._italic
        self.font_xlsx.italic = self._italic
    
    @property
    def underline(self):
        return self._underline
    
    @underline.setter
    def underline(self, underline):
        if underline == self.UNDERLINE_SINGLE or \
                underline == self.UNDERLINE_SINGLE_ACCOUNTING or \
                underline == self.UNDERLINE_DOUBLE or \
                underline == self.UNDERLINE_DOUBLE_ACCOUNTING:
            self._underline = underline
            self.font_xls.underline = True
            self.font_xlsx.underline = self._underline
        else:
            self._underline = 'none'
            self.font_xls.underline = False
            self.font_xlsx.underline = self._underline

    @property
    def strike(self):
        return self._strike
    
    @strike.setter
    def strike(self, strike):
        self._strike = strike
        self.font_xls.struck_out = self._strike
        self.font_xlsx.strike = self._strike
    
    def init_xls(self, font):
        rice_font = RiceFont()
        rice_font.name = font.name
        rice_font.color_index = font.colour_index % 64 if font.colour_index != 32767 else 0
        rice_font.size = font.height / 20
        rice_font.bold = True if font.bold else False
        rice_font.italic = True if font.italic else False
        rice_font.underline = rice_font.UNDERLINE_SINGLE if font.underline else 'none'
        rice_font.strike = True if font.struck_out else False
        return rice_font
    
    def init_xlsx(self, font):
        rice_font = RiceFont()
        rice_font.name = font.name
        color = get_color_rgb(font.color)
        rice_font.color = color
        rice_font.size = font.size
        rice_font.bold = font.bold
        rice_font.italic = font.italic
        rice_font.underline = font.underline
        rice_font.strike = font.strike
        return rice_font

    def __init__(self):
        self.font_xls = xlwt.Font()
        self.font_xlsx = Font()