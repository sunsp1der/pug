"""wx specific constants for use with the pug system AND generic pug constants
"""

from pug.constants import *

from wx import ALIGN_RIGHT, ALIGN_LEFT, Size

# miscellaneous sizes
WX_TEXTEDIT_LABEL_YOFFSET = 3
WX_PUGLIST_YSPACER = 0
WX_STANDARD_HEIGHT = 24
WX_BUTTON_BMP_SIZE = (16,16)
WX_BUTTON_SIZE = (28,WX_STANDARD_HEIGHT)

WX_DEFAULT_LABEL_ALIGNMENT = ALIGN_LEFT

WX_PUGFRAME_DEFAULT_SIZE = Size(PUGFRAME_DEFAULT_SIZE[0],
                                   PUGFRAME_DEFAULT_SIZE[1])

WX_SCROLLBAR_FUDGE = (16,0)