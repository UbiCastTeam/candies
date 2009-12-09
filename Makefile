install:
	python setup.py build && sudo python setup.py install

uninstall:
	sudo rm -vrf /usr/lib/python2.5/site-packages/candies2
	sudo rm -v /usr/lib/python2.5/site-packages/candies2*.egg-info

clean:
	rm -vrf build
