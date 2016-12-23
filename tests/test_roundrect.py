from gi.repository import Clutter
import candies2


if __name__ == '__main__':
    stage = Clutter.Stage()

    class Tester:
        def __init__(self):
            self.status = True

        def toggle_show(self, texture):
            if self.status: 
                print "\nset opacity 30"
                texture.set_opacity(30)
                print texture.get_opacity()
                texture.queue_redraw()
            else:
                print "\nset opacity 255"
                texture.set_opacity(255)
                print texture.get_opacity()
                texture.queue_redraw()
                print texture.get_property('color')
            self.status = not self.status
            return True

    t = Tester()

    stage.connect('destroy', Clutter.main_quit)

    texture = candies2.RoundRectangle()
    texture.set_size(200, 200)
    texture.set_border_radius(10)
    stage.add(texture)

    print texture.get_property('color')
    import gobject
    gobject.timeout_add(200, t.toggle_show, texture)

    stage.show()
    Clutter.main()
