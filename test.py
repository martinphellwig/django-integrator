# Copyright (c) 2016, Martin P. Hellwig, All Rights Reserved.
"""
Unit Test module
"""
# pylint:disable=R0904,C0111,W0212
import unittest
import os
import sys
import tempfile
import shutil
from django_integrator_script import create, make_application

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

    def test_content(self):
        tmp = list()
        create.main(self.cfg, self.tempdir)
        for entry in os.walk(self.tempdir):
            for item in entry[2]:
                path = os.path.join(entry[0], item)
                if not path.endswith('.pyc'):
                    tmp.append(path)

        self.assertEqual(29, len(tmp))

    def test_cli_script(self):
        tmp = list()
        def mock(configuration):
            tmp.append(configuration)

        namespace = type('create', (object,), {})()
        namespace.main = mock
        create_original = make_application.create
        make_application.create = namespace
        argv_orig = sys.argv[::]
        sys.argv = ['test', 'test', 'Test', 'test', 'Tester', 't@example.com']
        make_application.main()
        make_application.create = create_original
        sys.argv = argv_orig
        self.assertEqual(5, len(tmp[0]))



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
