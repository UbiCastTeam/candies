from gi.repository import Clutter
import random
import time

stage = Clutter.Stage()
stage.connect('destroy', Clutter.main_quit)

coef = 1
tic = time.time()
for x in xrange(640/coef):
    print 'Generating line %d...' %(x)
    for y in xrange(480/coef):
        r = Clutter.Rectangle()
        color = Clutter.color_from_string(
            random.randint(0, 255), random.randint(0, 255),
            random.randint(0, 255), 255
        )
        r.set_color(color)
        r.set_position(x*coef, y*coef)
        r.set_size(coef, coef)
        stage.add(r)
tac = time.time()

print 'Generated in', tac - tic, 'seconds.'

stage.show()
Clutter.main()