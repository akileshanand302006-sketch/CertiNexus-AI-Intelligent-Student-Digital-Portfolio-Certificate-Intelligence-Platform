"""
CertiNexus AI — Backend ML Package Proxy & Namespace Extension
Extends backend.ml to include the root ml package modules.
"""

import sys
import os
import pkgutil

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

_root_ml = os.path.join(_root, "ml")
if os.path.exists(_root_ml) and _root_ml not in __path__:
    __path__.append(_root_ml)
