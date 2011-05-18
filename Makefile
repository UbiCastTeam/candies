#!/usr/bin/make -f

all: build

build:
	python setup.py build

install: build
	sudo python setup.py install

uninstall:
	sudo rm -vrf /usr/lib/python2.5/site-packages/candies2
	sudo rm -v /usr/lib/python2.5/site-packages/candies2*.egg-info

doc:
	epydoc --no-private --docformat restructuredtext --name candies2 --url http://candies.ubicast.eu candies2/ || true

clean:
	rm -rvf html/
	rm -vrf build
	find . -name '*~' | xargs rm -vf
	find . -name '*.py[co]' | xargs rm -fv
