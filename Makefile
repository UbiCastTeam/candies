#!/usr/bin/make -f

install:
	python setup.py build && sudo python setup.py install

uninstall:
	sudo rm -vrf /usr/lib/python2.5/site-packages/candies2
	sudo rm -v /usr/lib/python2.5/site-packages/candies2*.egg-info

doc:
	epydoc --no-private --docformat restructuredtext --name candies2 --url http://candies.ubicast.eu candies2/

clean:
	rm -rvf html/
	rm -vrf build
	find . -name '*.py[co]' | xargs rm -fv
