.PHONY: test

TUXPKG_MIN_COVERAGE ?= 100

test:
	python3 -m pytest --cov=$(PROJECT) --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=$(TUXPKG_MIN_COVERAGE)

style:
	black --check --diff .

flake8:
	flake8 --exclude=dist/ --ignore=E501,W503 .

typecheck:
	mypy --exclude=dist/ .

version ?= $(shell sed -e '/^__version__/ !d; s/"\s*$$//; s/.*"//' $(PROJECT)/__init__.py)

CLEAN += dist

rpm: dist/$(PROJECT)-$(version)-0$(PROJECT).noarch.rpm

RPMBUILD = rpmbuild
dist/$(PROJECT)-$(version)-0$(PROJECT).noarch.rpm: dist/$(PROJECT)-$(version).tar.gz dist/$(PROJECT).spec
	cd dist && \
	$(RPMBUILD) -ta --define "dist $(PROJECT)" --define "_rpmdir $$(pwd)" $(PROJECT)-$(version).tar.gz
	mv $(patsubst dist/%, dist/noarch/%, $@) $@
	rmdir dist/noarch

rpmsrc: dist dist/$(PROJECT).spec

dist/$(PROJECT).spec: $(PROJECT).spec
	cp $(PROJECT).spec dist/

dist: dist/$(PROJECT)-$(version).tar.gz

dist/$(PROJECT)-$(version).tar.gz:
	flit build

deb: debsrc dist/$(PROJECT)_$(version)-1_all.deb

dist/$(PROJECT)_$(version)-1_all.deb: dist/$(PROJECT)_$(version)-1.dsc
	cd dist/$(PROJECT)-$(version) && dpkg-buildpackage -b -us -uc

debsrc: dist dist/$(PROJECT)_$(version)-1.dsc dist/$(PROJECT)_$(version).orig.tar.gz

dist/$(PROJECT)_$(version).orig.tar.gz: dist/$(PROJECT)-$(version).tar.gz
	ln -f $< $@

dist/$(PROJECT)_$(version)-1.dsc: debian dist/$(PROJECT)_$(version).orig.tar.gz $(wildcard debian/*)
	cd dist && tar xaf $(PROJECT)_$(version).orig.tar.gz
	cp -r debian/ dist/$(PROJECT)-$(version)
	cd dist/$(PROJECT)-$(version)/ && dpkg-buildpackage -S -d -us -uc

CLEAN += run
run:
	echo "#!/bin/sh" > $@
	echo "set -eu" >> $@
	echo 'realfile="$$(readlink -f "$$0")"' >> $@
	echo 'export PYTHONPATH="$$(dirname "$$realfile")"' >> $@
	echo 'exec python3 -m $(PROJECT) "$$@"' >> $@
	chmod +x run

release:
	python3 -m tuxpkg release

clean::
	$(RM) -r $(CLEAN)
