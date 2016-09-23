from gi.repository import Clutter

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed'\
              ' do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
label = Clutter.Text()
label.set_text(lorem_ipsum)
print '----------------------------     --------------------------'
print '| Font size | Actor height |     | Font size | Actor size |'
print '----------------------------     --------------------------'

for size in range(1, 101):
    label.set_font_name('Sans %s' %(size))
    pt_height = label.get_height()
    label.set_font_name('Sans %spx' %(size))
    px_height = label.get_height()
    print '|   %3dpt   |     %3dpx    |  %.2f   |   %3dpx   |    %3dpx   | %.2f' \
                                            %(size, pt_height, pt_height/size, size, px_height, px_height/size)

print '----------------------------     --------------------------'