import clutter
import random
import time

stage = clutter.Stage()
stage.connect('destroy', clutter.main_quit)

coef = 1
tic = time.time()
for x in xrange(640/coef):
    print 'Generating line %d...' %(x)
    for y in xrange(480/coef):
        r = clutter.Rectangle()
        color = clutter.Color(
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
clutter.main()