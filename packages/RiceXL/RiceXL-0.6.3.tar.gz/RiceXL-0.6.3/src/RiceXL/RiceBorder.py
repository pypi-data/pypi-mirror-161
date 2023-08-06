import xlwt
from openpyxl.styles import Border, Side
from openpyxl.styles.colors import COLOR_INDEX
from RiceXL.RiceUtils import get_color_rgb, get_color_rgb_by_index

BORDER_STYLE = (
    'none', #0
    'thin', #1
    'medium', #2
    'dashed', #3
    'dotted', #4
    'thick', #5
    'double', #6
    'hair', #7
    'mediumDashed', #8
    'dashDot', #9
    'mediumDashDot', #10
    'dashDotDot', #11
    'mediumDashDotDot', #12
    'slantDashDot' #13
)

class RiceBorder():
    _border_style_left = None
    _border_style_right = None
    _border_style_top = None
    _border_style_bottom = None
    _border_style_all = None
    _border_color_left = None
    _border_color_right = None
    _border_color_top = None
    _border_color_bottom = None
    _border_color_all = None
    _side_left = Side()
    _side_right = Side()
    _side_top = Side()
    _side_bottom = Side()
    _side_all = Side()

    @property
    def border_style_left(self):
        return self._border_style_left
    
    @border_style_left.setter
    def border_style_left(self, border_style):
        self._border_style_left = border_style
        self._border_style_all = None
        self.border_xls.left = BORDER_STYLE.index(self._border_style_left)
        if self.border_xlsx.left is not None:
            self._side_left = self.border_xlsx.left
        else:
            self.border_xlsx.left = self._side_left
        # Side().border_style <==> Side().style
        self._side_left.border_style = self._border_style_left
    
    @property
    def border_style_right(self):
        return self._border_style_right

    @border_style_right.setter
    def border_style_right(self, border_style):
        self._border_style_right = border_style
        self._border_style_all = None
        self.border_xls.right = BORDER_STYLE.index(self._border_style_right)
        if self.border_xlsx.right is not None:
            self._side_right = self.border_xlsx.right
        else:
            self.border_xlsx.right = self._side_right
        self._side_right.border_style = self._border_style_right

    @property
    def border_style_top(self):
        return self._border_style_top

    @border_style_top.setter
    def border_style_top(self, border_style):
        self._border_style_top = border_style
        self._border_style_all = None
        self.border_xls.top = BORDER_STYLE.index(self._border_style_top)
        if self.border_xlsx.top is not None:
            self._side_top = self.border_xlsx.top
        else:
            self.border_xlsx.top = self._side_top
        self._side_top.border_style = self._border_style_top
    
    @property
    def border_style_bottom(self):
        return self._border_style_bottom

    @border_style_bottom.setter
    def border_style_bottom(self, border_style):
        self._border_style_bottom = border_style
        self._border_style_all = None
        self.border_xls.bottom = BORDER_STYLE.index(self._border_style_bottom)
        if self.border_xlsx.bottom is not None:
            self._side_bottom = self.border_xlsx.bottom
        else:
            self.border_xlsx.bottom = self._side_bottom
        self._side_bottom.border_style = self._border_style_bottom
    
    @property
    def border_style_all(self):
        return self._border_style_all

    @border_style_all.setter
    def border_style_all(self, border_style):
        self.border_style_left = border_style
        self.border_style_right = border_style
        self.border_style_top = border_style
        self.border_style_bottom = border_style
        # self._border_style_all must be set in the end,
        # or it would be set as None by the other properties.
        self._border_style_all = border_style
    
    @property
    def border_color_left(self):
        return self._border_color_left

    @border_color_left.setter
    def border_color_left(self, border_color):
        self._border_color_left = border_color
        self._border_color_all = None
        self.border_xls.left_colour = COLOR_INDEX.index(self._border_color_left)
        if self.border_xlsx.left is not None:
            self._side_left = self.border_xlsx.left
        else:
            self.border_xlsx.left = self._side_left
        self._side_left.color = self._border_color_left
    
    @property
    def border_color_right(self):
        return self._border_color_right

    @border_color_right.setter
    def border_color_right(self, border_color):
        self._border_color_right = border_color
        self._border_color_all = None
        self.border_xls.right_colour = COLOR_INDEX.index(self._border_color_right)
        if self.border_xlsx.right is not None:
            self._side_right = self.border_xlsx.right
        else:
            self.border_xlsx.right = self._side_right
        self._side_right.color = self._border_color_right
    
    @property
    def border_color_top(self):
        return self._border_color_top

    @border_color_top.setter
    def border_color_top(self, border_color):
        self._border_color_top = border_color
        self._border_color_all = None
        self.border_xls.top_colour = COLOR_INDEX.index(self._border_color_top)
        if self.border_xlsx.top is not None:
            self._side_top = self.border_xlsx.top
        else:
            self.border_xlsx.top = self._side_top
        self._side_top.color = self._border_color_top
    
    @property
    def border_color_bottom(self):
        return self._border_color_bottom

    @border_color_bottom.setter
    def border_color_bottom(self, border_color):
        self._border_color_bottom = border_color
        self._border_color_all = None
        self.border_xls.bottom_colour = COLOR_INDEX.index(self._border_color_bottom)
        if self.border_xlsx.bottom is not None:
            self._side_bottom = self.border_xlsx.bottom
        else:
            self.border_xlsx.bottom = self._side_bottom
        self._side_bottom.color = self._border_color_bottom
    
    @property
    def border_color_all(self):
        return self._border_color_all
    
    @border_color_all.setter
    def border_color_all(self, border_color):
        self.border_color_left = border_color
        self.border_color_right = border_color
        self.border_color_top = border_color
        self.border_color_bottom = border_color
        # self._border_color_all must be set in the end,
        # or it would be set as None by the other properties.
        self._border_color_all = border_color
    
    def init_xls(self, border):
        rice_border = RiceBorder()
        rice_border.border_style_left = BORDER_STYLE[border.left]
        rice_border.border_style_right = BORDER_STYLE[border.right]
        rice_border.border_style_top = BORDER_STYLE[border.top]
        rice_border.border_style_bottom = BORDER_STYLE[border.bottom]
        rice_border.border_color_left = get_color_rgb_by_index(border.left_colour)
        rice_border.border_color_right = get_color_rgb_by_index(border.right_colour)
        rice_border.border_color_top = get_color_rgb_by_index(border.top_colour)
        rice_border.border_color_bottom = get_color_rgb_by_index(border.bottom_colour)
        return rice_border
    
    def init_xlsx(self, border):
        rice_border = RiceBorder()
        side_left = border.left
        side_right = border.right
        side_top = border.top
        side_bottom = border.bottom
        rice_border.border_style_left = side_left.border_style if side_left.border_style is not None else 'none'
        rice_border.border_style_right = side_right.border_style if side_right.border_style is not None else 'none'
        rice_border.border_style_top = side_top.border_style if side_top.border_style is not None else 'none'
        rice_border.border_style_bottom = side_bottom.border_style if side_bottom.border_style is not None else 'none'
        rice_border.border_color_left = get_color_rgb(side_left.color) if side_left.color is not None else '00000000'
        rice_border.border_color_right = get_color_rgb(side_right.color) if side_right.color is not None else '00000000'
        rice_border.border_color_top = get_color_rgb(side_top.color) if side_top.color is not None else '00000000'
        rice_border.border_color_bottom = get_color_rgb(side_bottom.color) if side_bottom.color is not None else '00000000'
        return rice_border

    def __init__(self):
        self.border_xls = xlwt.Borders()
        self.border_xlsx = Border()