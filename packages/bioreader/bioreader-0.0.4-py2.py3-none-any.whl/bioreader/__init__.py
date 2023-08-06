"""Bio file readers, instrument schema.

Import the package::

   import bioreader

This is the complete API reference:

.. autosummary::
   :toctree: .

   readout_type
   readout_platform
"""

__version__ = "0.0.4"  # denote a pre-release for 0.1.0 with 0.1a1

from . import lookup  # noqa
from ._core import readout_platform, readout_type  # noqa
