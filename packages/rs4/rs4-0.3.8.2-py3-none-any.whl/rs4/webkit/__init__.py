
from ..annotations import Uninstalled
from hashlib import md5

try:
    from .drivers import Chrome, Firefox, IE
except ModuleNotFoundError:
    IE = Firefox = Chrome = Uninstalled ('selenium')

try:
    from .nops import nops
except ModuleNotFoundError:
    nops = Uninstalled ('cssselect==0.9.1, lxml==4.4.0 and html5lib==0.999999999')

from .webtest import Target
Site = Target
