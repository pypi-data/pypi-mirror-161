from .utillc import *
from .utillc import utillc_version
try :
    from .qtp  import video
except :
    print ("no qt5")
#from .expression import *

__version__ = utillc_version
