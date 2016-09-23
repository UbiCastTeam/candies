'''
import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter

if __name__ == '__main__':
    stage = Clutter.Stage()

    def toggle_show(texture):
        if texture.get_property('visible'):
            texture.hide()
            #texture.unparent()
            stage.remove(texture)
        else:
            #texture.set_parent(stage)
            stage.add(texture)
            texture.show()
        return True

    stage.connect('destroy', Clutter.main_quit)

    # texture = Clutter.Texture('candies.png')
    # texture = Clutter.Texture.new_from_file('candies.png')
    texture = Clutter.Texture.new_from_file('/home/ubicast/projects/candies/tests/candies.png')
    stage.add_child(texture)
    # texture.set_size( 400,400) 
    #stage.add(texture)
    # Clutter.Container.add_actor(stage, texture)

    # import gobject
    # gobject.timeout_add(200, toggle_show, texture)

    stage.show()
    Clutter.main()
'''

#!/usr/bin/env python
# import cairo
import gi


gi.require_version('Clutter', '1.0')
from gi.repository import Clutter


if __name__ == '__main__':

    def stage_key(element, event):

        if event.keyval == Clutter.Escape:

            clutter_quit()


    def clutter_quit(*args):

        Clutter.main_quit()



    Clutter.init()

    stage = Clutter.Stage()

    stage.set_size(500, 500)

    stage.set_title('Clutter - SVG Content')

    stage.set_background_color(Clutter.color_from_string('white')[1])



    texture = Clutter.Texture.new_from_file('/home/ubicast/projects/candies/tests/candies.png')

    stage.add_child(texture)



    # quit when the window gets closed

    stage.connect('destroy', clutter_quit)



    # close window on escape

    stage.connect('key-press-event', stage_key)



    stage.show()

    Clutter.main()