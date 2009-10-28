#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clutter
import os
import gobject
from candies2.progressbar import SkinnedProgressBar as ProgressBar

__path__ = os.path.dirname(os.path.abspath(__file__))

stage = clutter.Stage()
stage.connect('destroy', clutter.main_quit)

# Animated progress bar
label = clutter.Text()
label.set_position(5, 5)
label.set_text('Click on the progress bar bellow...')
stage.add(label)

bar = ProgressBar(os.path.join(__path__, 'progress_skin'))
bar.props.progression = 0.0
bar.set_position(5, 20)
bar.set_size(630, 50)
def update_label(bar, event, label):
    label.set_text('%d %%' %(bar.props.progression * 100))
def progress(bar):
    bar.props.progression = min(round(bar.props.progression + 0.002, 3), 1.0)
    return bar.props.progression < 1.0
def on_button_press(bar, event):
    bar.props.progression = 0.0
    gobject.timeout_add(10, progress, bar)
bar.set_reactive(True)
bar.connect('button-press-event', on_button_press)
bar.connect('notify::progression', update_label, label)
stage.add(bar)

# Static 0%
label = clutter.Text()
label.set_position(5, 100)
label.set_text('0 %')
stage.add(label)

bar = ProgressBar(os.path.join(__path__, 'progress_skin'))
bar.props.progression = 0.0
bar.set_position(5, 115)
bar.set_size(630, 50)
stage.add(bar)

# Static 67%
label = clutter.Text()
label.set_position(5, 200)
label.set_text('67 %')
stage.add(label)

bar = ProgressBar(os.path.join(__path__, 'progress_skin'))
bar.props.progression = 0.667
bar.set_position(5, 215)
bar.set_size(630, 50)
stage.add(bar)

# Static 100%
label = clutter.Text()
label.set_position(5, 300)
label.set_text('100 %')
stage.add(label)

bar = ProgressBar(os.path.join(__path__, 'progress_skin'))
bar.props.progression = 1.0
bar.set_position(5, 315)
bar.set_size(630, 50)
stage.add(bar)

stage.show()
clutter.main()