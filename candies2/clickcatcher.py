#!/usr/bin/env python
# -*- coding: utf-8 -*

from gi.repository import Clutter
from container import BaseContainer
from disk import Disk


class ClickCatcher(BaseContainer):
    __gtype_name__ = 'ClickCatcher'

    def __init__(self, actor=None, circles_radius=60, circles_color='#ff8888aa', click_callback=None):
        BaseContainer.__init__(self, allow_add=False, allow_remove=False)
        self._actor = None
        if actor:
            self.set_actor(actor)

        self.click_callback = click_callback

        self._circle_radius = circles_radius
        self._circle_center = 0, 0
        self._circle = Disk()
        self._circle.set_opacity(0)
        self._circle.set_color(circles_color)
        self._circle.set_stroke_width(10)
        self._circle.move_anchor_point_from_gravity(Clutter.GRAVITY_CENTER)
        self._add(self._circle)

        self._inner_circle_radius = self._circle_radius / 2.0
        self._inner_circle = Disk()
        self._inner_circle.set_opacity(0)
        self._inner_circle.set_color(circles_color)
        self._inner_circle.set_stroke_width(7)
        self._inner_circle.move_anchor_point_from_gravity(
            Clutter.GRAVITY_CENTER)
        self._add(self._inner_circle)

        self._timeline = Clutter.Timeline(duration=500)
        self._timeline.connect('completed', self._on_timeline_completed)
        self._timeline_completed = True

        alpha = Clutter.Alpha(self._timeline, Clutter.LINEAR)

        self.alpha_behaviour = Clutter.BehaviourOpacity(
            opacity_start=255, opacity_end=0, alpha=alpha)
        self.alpha_behaviour.apply(self._circle)
        self.alpha_behaviour.apply(self._inner_circle)
        self.scale_behaviour = Clutter.BehaviourScale(
            0.0, 0.0, 1.0, 1.0, alpha=alpha)
        self.scale_behaviour.apply(self._circle)
        self.scale_behaviour.apply(self._inner_circle)

        self.set_reactive(True)
        self.connect('button-press-event', self._on_press)
        self.connect('button-release-event', self._on_release)

    def _on_timeline_completed(self, timeline):
        self._timeline_completed = True

    def _on_press(self, source, event):
        if not self._timeline_completed:
            self._timeline.stop()
        self._circle_center = event.x, event.y
        if self.click_callback is not None:
            self.click_callback(event.x, event.y)
        self.queue_relayout()
        self._timeline.start()
        self._timeline_completed = False

    def _on_release(self, source, event):
        if self._timeline_completed:
            self._circle_center = event.x, event.y
            self.queue_relayout()
            self._timeline.start()
            self._timeline_completed = False

    def set_actor(self, actor):
        self._add(actor)
        self._actor = actor

    def do_get_preferred_width(self, for_height):
        if self._actor:
            return self._actor.get_preferred_width(for_height=for_height)
        else:
            return 0, 0

    def do_get_preferred_height(self, for_width):
        if self._actor:
            return self._actor.get_preferred_height(for_width=for_width)
        else:
            return 0, 0

    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1

        cbox = Clutter.ActorBox()
        cbox.x1 = self._circle_center[0]
        cbox.y1 = self._circle_center[1]
        cbox.x2 = cbox.x1 + 2 * self._circle_radius
        cbox.y2 = cbox.y1 + 2 * self._circle_radius
        self._circle.allocate(cbox, flags)

        icbox = Clutter.ActorBox()
        icbox.x1 = self._circle_center[0]
        icbox.y1 = self._circle_center[1]
        icbox.x2 = cbox.x1 + 2 * self._inner_circle_radius
        icbox.y2 = cbox.y1 + 2 * self._inner_circle_radius
        self._inner_circle.allocate(icbox, flags)

        if self._actor:
            abox = Clutter.ActorBox(0, 0, width, height)
            self._actor.allocate(abox, flags)

        Clutter.Actor.do_allocate(self, box, flags)


if __name__ == '__main__':
    # stage
    stage = Clutter.Stage()
    stage_width = 1200
    stage_height = 600
    stage.set_size(stage_width, stage_height)
    stage.set_color('#000000ff')
    stage.connect('destroy', Clutter.main_quit)

    bg = Clutter.Rectangle()
    bg.set_color('#000000ff')

    def on_bg_press(source, event):
        print 'press on bg'

    def on_bg_release(source, event):
        print 'release on bg'

    bg.set_reactive(True)
    bg.connect('button-press-event', on_bg_press)
    bg.connect('button-release-event', on_bg_release)

    catcher = ClickCatcher(bg)
    catcher.set_size(1200, 600)
    stage.add(catcher)

    stage.show()
    Clutter.main()
