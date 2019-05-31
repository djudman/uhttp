import coverage
import unittest

cov = coverage.Coverage()
cov.start()
unittest.main(module='test_app')
cov.stop()
cov.save()
cov.html_report()
