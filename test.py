# Copyright (c) 2016, Martin P. Hellwig, All Rights Reserved.
"""
"""
# pylint:disable=R0904,C0111,W0212
import unittest
import os
import tempfile
import shutil
from django_integrator_script import create

class Test(unittest.TestCase):
    def setUp(self):
        self.cfg = {'name':'django-integrator-testname',
                    'class':'DjangoIntegratorTestname',
                    'verbose':'Test Application',
                    'author':'Firstname Lastname',
                    'email':'first.last@example.com'}
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_no_apps_py(self):
        create.main(self.cfg, self.tempdir)
        path = os.path.join(self.tempdir, self.cfg['name'],
                            self.cfg['django_app_name'])
        self.assertNotIn('apps.py', os.listdir(path=path))

    def test_check_pypi(self):
        tmp = self.cfg.copy()
        tmp['name'] = 'django-integrator'
        self.assertRaises(ValueError, create._check_pypi, tmp)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()