#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clutter
import os
from candies2.progressbar import ProgressBar

__path__ = os.path.dirname(os.path.abspath(__file__))

stage = clutter.Stage()
stage.connect('destroy', clutter.main_quit)

bar = ProgressBar(os.path.join(__path__, 'progress_skin'))
bar.set_size(600, 120)
stage.add(bar)
bar.show()

stage.show()
clutter.main()