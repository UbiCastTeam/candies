#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
from distutils.core import setup

from candies2.version import VERSION

setup(
    name="candies2",
    version=VERSION,
    description="candies is an opengl touch-oriented GUI toolkit",
    author="Damien Boucard, Florent Thiery",
    author_email="candies [AT] ubicast [DOT] eu",
    url="http://candies.ubicast.eu/",
    license="GNU/LGPLv3",
    packages = ['candies2'],
)

