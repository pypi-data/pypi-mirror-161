# -*- coding: utf-8 -*-
"""
Sub-package containing the formats and the actions related to EAD (Encoded
Archival Description).

EAD exists in two main formats : EAD-2002 and Ape-EAD. The various actions
defined here can be used to convert files in EAD-2002 into Ape-EAD that has
more constraints. Both formats rely on XML files.
"""

import os.path as osp
import json

from .registration import register  # noqa


def ead2_to_ape_default_settings():
    """load default ead2 -> ape transformation settings"""
    settings_filepath = osp.join(
        osp.dirname(__file__), "default-ead2-to-ape-settings.json"
    )
    with open(settings_filepath) as inputf:
        return json.load(inputf)
