import coverage
import unittest

cov = coverage.Coverage()
cov.start()
unittest.main(module='test_app', verbosity=2)
cov.stop()
cov.save()
cov.html_report()
