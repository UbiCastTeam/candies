#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
from distutils.core import setup

candies = imp.load_source("version", "candies2/version.py")

setup(
    name="candies2",
    version=candies.VERSION,
    description="candies is an opengl touch-oriented GUI toolkit",
    author="Damien Boucard, Florent Thiery",
    author_email="candies [AT] ubicast [DOT] eu",
    url="http://candies.ubicast.eu/",
    license="GNU/LGPLv3",
    packages = ['candies2'],
)

