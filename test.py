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

class Test001Script(unittest.TestCase):
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

def _setup():
    cfg = {'name':'django-integrator-testname',
           'class':'DjangoIntegratorTestname',
           'verbose':'Test Application',
           'author':'Firstname Lastname',
           'email':'first.last@example.com'}

    cfg['tmp'] = tempfile.mkdtemp()

    create.main(cfg, cfg['tmp'])
    path = os.path.join(cfg['tmp'], cfg['name'])
    sys.path.insert(0, path)
    cfg['settings_orig'] = os.environ.get('DJANGO_SETTINGS_MODULE', None)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'interface.settings'

    # remove the last lines in the settings file that import django_integrator
    file_path = os.path.join(path, 'interface', 'settings.py')
    with open(file_path, 'r+') as file_open:
        tmp = file_open.readlines()[:-4]
        file_open.seek(0)
        file_open.truncate()
        for line in tmp:
            file_open.write(line)
            
    # Will need to change the app settings.py to add an APP.

    return cfg

def _teardown(cfg):
    sys.path.pop(0)
    shutil.rmtree(cfg['tmp'])

    if cfg['settings_orig'] is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = cfg['settings_orig']
    else:
        os.environ.pop('DJANGO_SETTINGS_MODULE')


class Test002Integrator(unittest.TestCase):
    def setUp(self):
        self.cfg = _setup()

    def tearDown(self):
        _teardown(self.cfg)

    def test_000(self):
        import django_integrator
        import django_integrator.main
        django_integrator.add_application(self.cfg['django_app_name'])
        settings = self.cfg['django_app_name'] + '.settings'
        django_integrator.add_settings(settings)
        tmp = list()
        django_integrator.add_urlpatterns(tmp)
        key = 'INSTALLED_APPS'
        one = django_integrator.main._IMPORTER.settings['TARGET'][key][::]
        print(django_integrator.main._IMPORTER.settings['ORIGIN'])
        django_integrator.main._IMPORTER.restore(key)
        
        two = django_integrator.main._IMPORTER.settings['TARGET'][key][::]
        self.assertNotEqual(one, two)

        print(one)
        



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
