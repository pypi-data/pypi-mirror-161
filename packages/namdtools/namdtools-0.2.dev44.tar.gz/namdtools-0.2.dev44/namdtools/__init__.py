
from . import analysis
from .analysis import *

from . import core
from .core import *

from . import io
from .io import *


# from .core import namd
# from namdtools.core import *

__all__ = analysis.__all__
__all__.extend(core.__all__)
__all__.extend(io.__all__)
# __all__.extend(namd.__all__)


# import sys

# this = sys.modules[__name__]

# this.charmrun = None
# this.namd = 'namd2'
