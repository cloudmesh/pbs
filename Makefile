all:
	python setup.py install
	sphinx-apidoc -o docs/source cloudmesh_pbs
	cd docs; make -f Makefile html

view:
	open docs/build/html/index.html
