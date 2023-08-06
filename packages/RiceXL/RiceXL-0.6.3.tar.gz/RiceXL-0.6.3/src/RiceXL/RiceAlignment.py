import xlwt
from openpyxl.styles import Alignment

HORIZONTAL = (
    'general', #0
    'left', #1
    'center', #2
    'right', #3
    'fill', #4
    'justify', #5
    'centerContinuous', #6
    'distributed' #7
)

VERTICAL = (
    'top', #0
    'center', #1
    'bottom', #2
    'justify', #3
    'distributed' #4
)

class RiceAlignment():
    _horizontal = None
    _vertical = None
    _wrap = None

    @property
    def horizontal(self):
        return self._horizontal
    
    @horizontal.setter
    def horizontal(self, horizontal):
        self._horizontal = horizontal
        self.alignment_xls.horz = HORIZONTAL.index(horizontal)
        self.alignment_xlsx.horizontal = horizontal
    
    @property
    def vertical(self):
        return self._vertical
    
    @vertical.setter
    def vertical(self, vertical):
        self._vertical = vertical
        self.alignment_xls.vert = VERTICAL.index(vertical)
        self.alignment_xlsx.vertical = vertical
    
    @property
    def wrap(self):
        return self._wrap
    
    @wrap.setter
    def wrap(self, wrap):
        self._wrap = wrap
        self.alignment_xls.wrap = 1 if self._wrap else 0
        self.alignment_xlsx.wrap_text = wrap
    
    def init_xls(self, alignment):
        rice_alignment = RiceAlignment()
        rice_alignment.horizontal = HORIZONTAL[alignment.horz]
        rice_alignment.vertical = VERTICAL[alignment.vert]
        rice_alignment.wrap = True if alignment.wrap else False
        return rice_alignment
    
    def init_xlsx(self, alignment):
        rice_alignment = RiceAlignment()
        rice_alignment.horizontal = alignment.horizontal if alignment.horizontal is not None else 'general'
        rice_alignment.vertical = alignment.vertical if alignment.vertical is not None else 'top'
        rice_alignment.wrap = alignment.wrap_text if alignment.wrap_text is not None else False
        return rice_alignment

    def __init__(self):
        self.alignment_xls = xlwt.Alignment()
        self.alignment_xlsx = Alignment()