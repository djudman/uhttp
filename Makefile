all:
	@python3 setup.py sdist
install:
	@python3 setup.py install
echo-app:
	@PWD=$(pwd)
	@PYTHONPATH="$(PWD)" python3 ./examples/echoapp/httpd.py
time-app:
	@PWD=$(pwd)
	@PYTHONPATH="$(PWD):$(PWD)/examples/timeapp" python3 ./examples/timeapp/httpd.py
test:
	@PWD=$(pwd)
	@cd ./tests && PYTHONPATH="$(PWD)" python3 -m unittest
