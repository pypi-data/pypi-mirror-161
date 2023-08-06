from .pysnirf2 import *
from .__version__ import __version__ as __version__

from warnings import warn
warn("Installation of this library via the pysnirf2 remote is deprecated after v0.7.3. Install future versions using `pip install snirf`.",
         category=DeprecationWarning,
         stacklevel=2)