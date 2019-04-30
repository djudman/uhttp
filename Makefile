echo-app:
	@PWD=$(pwd)
	@PYTHONPATH="$(PWD)" python3 ./examples/echoapp/httpd.py
time-app:
	@PWD=$(pwd)
	@PYTHONPATH="$(PWD):$(PWD)/examples/timeapp" python3 ./examples/timeapp/httpd.py
test:
	@python3 ./tests/run.py
