number = 14046
name = pinger
hslfile = $(number)_$(name).hsl

release/$(hslfile): config.xml src/*.py
	docker run --volume $(shell pwd):/hsl/projects/$(name) --workdir /hsl lindra/gira /usr/bin/python2 generator.pyc $(name)

clean:
	rm -f release/$(hslfile)

zip: release/$(hslfile)
	zip $^.zip $^
