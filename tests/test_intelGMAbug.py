import clutter

if __name__ == '__main__':
    stage = clutter.Stage()

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

    stage.connect('destroy', clutter.main_quit)

    texture = clutter.Texture('candies.png')
    stage.add(texture)

    import gobject
    gobject.timeout_add(200, toggle_show, texture)

    stage.show()
    clutter.main()
