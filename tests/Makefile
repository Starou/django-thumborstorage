coveralls:
	# There is no way to tell coveralls to run runtests.py.
	# Maybe the --config-file?
	# This generate the .coverage report file (default).
	@coverage run --rcfile=coveragerc runtests.py
	@coveralls -y coveralls.yaml -d .coverage
