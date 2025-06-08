number = 14046
name = pinger

include ../docker-setup.mk

$(hslfile): config.xml src/*.py
	$(python2) generator.pyc $(name)

clean:
	rm -f $(hslfile)

zip: $(hslfile)
	zip $^.zip $^
