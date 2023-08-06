# -*- coding: utf-8 -*-

try:
    from onion_config.config_base import ConfigBase, __version__
except ImportError:
    from .config_base import ConfigBase, __version__
