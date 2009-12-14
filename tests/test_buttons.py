import os
import clutter
import candies2

__path__ = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)

    # Test basis
    item1 = candies2.ItemButton('Item1')
    item1.set_size(150, 150)
    item1.set_position(50, 50)
    item1.connect('button-press-event', lambda s,e: item1.toggle_status())
    stage.add(item1)
    
    # Test opacity
    back = clutter.Texture(os.path.join(__path__, 'candies.png'))
    back.set_size(back.get_preferred_width(150)[1], 150)
    back.set_position(250, 50)
    stage.add(back)
    
    item2 = candies2.ItemButton('Item2')
    item2.props.color = '#00000000'
    item2.props.active_color = '#80808040'
    item2.set_size(150, 150)
    item2.set_position(225, 50)
    item2.connect('button-press-event', lambda s,e: item2.toggle_status())
    stage.add(item2)

    # Test button with a picture
    item3 = candies2.ItemButton('Item3', os.path.join(__path__, 'logo.png'))
    item3.props.color = '#00000000'
    item3.props.active_color = '#80808040'
    item3.set_size(150, 150)
    item3.set_position(50, 225)
    item3.connect('button-press-event', lambda s,e: item3.toggle_status())
    stage.add(item3)
    
    # Test button with a picture a little too big
    item4 = candies2.ItemButton('Item4', os.path.join(__path__, 'logo.png'))
    item4.props.color = '#00000000'
    item4.props.active_color = '#80808040'
    item4.set_size(109, 113)
    item4.set_position(225, 225)
    item4.connect('button-press-event', lambda s,e: item4.toggle_status())
    stage.add(item4)
    
    # Test button with a picture really too big
    item4 = candies2.ItemButton('Item4', os.path.join(__path__, 'logo.png'))
    item4.props.color = '#00000000'
    item4.props.active_color = '#80808040'
    item4.set_size(90, 90)
    item4.set_position(359, 225)
    item4.connect('button-press-event', lambda s,e: item4.toggle_status())
    stage.add(item4)

    image_path = os.path.join(__path__, 'candies.png')
    b = candies2.ImageButton('Test image', image_path, stretch=False,
                                                          image_proportion=0.5)
    b.props.color = 'Pink'
    b.set_size(100, 100)
    b.set_position(425, 380)
    stage.add(b)

    def callback(source, event):
        print 'Button clicked'

    image_path = os.path.join(__path__, 'candies_vert.png')
    b = candies2.ImageButton("Test vertical image", image_path, stretch=False,
                                          image_proportion=0.8, activable=True)
    b.props.color = '#00ffff44'
    b.props.border_color = '#ff00ff44'
    b.set_size(100, 100)
    b.set_position(530, 380)
    b.connect('button-press-event', callback)
    stage.add(b)
    
    
    stage.show()
    clutter.main()
