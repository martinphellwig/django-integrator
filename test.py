# Copyright (c) 2016, Martin P. Hellwig, All Rights Reserved.
"""
Unit Test module
"""
# pylint:disable=R0904,C0111,W0212
import unittest
import sys
import os
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

def _strip_interface_settings(path):
    """
    Strip the last lines in the settings file that have the django
    integrator settings defined."""
    file_path = os.path.join(path, 'interface', 'settings.py')
    with open(file_path, 'r+') as file_open:
        tmp = file_open.readlines()[:-4]
        file_open.seek(0)
        file_open.truncate()
        for line in tmp:
            file_open.write(line)

def _modify_app_settings(cfg):
    "Modify the app settings for testing purposes"
    path = os.path.join(cfg['tmp'], cfg['name'], cfg['django_app_name'],
                        'settings.py')

    with open(path, 'r+') as file_open:
        file_open.seek(0, 2)
        file_open.write("INSTALLED_APPS=['django.contrib.humanize']\n")
        file_open.write("SOME_LOCAL_VAR='var'\n")
        file_open.write("DATABASES={'cenvars':"
                        "{'ENGINE':'django.db.backends.sqlite3',"
                        "'NAME':':memory:'}}\n")

def _setup():
    cfg = {'name':'django-integrator-testname',
           'class':'DjangoIntegratorTestname',
           'verbose':'Test Application',
           'author':'Firstname Lastname',
           'email':'first.last@example.com',
           'tmp':tempfile.mkdtemp()}

    create.main(cfg, cfg['tmp'])
    path = os.path.join(cfg['tmp'], cfg['name'])
    sys.path.insert(0, path)
    cfg['settings_orig'] = os.environ.get('DJANGO_SETTINGS_MODULE', None)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'interface.settings'

    _strip_interface_settings(path)
    _modify_app_settings(cfg)

    return cfg

def _teardown(cfg):
    sys.path.pop(0)
    shutil.rmtree(cfg['tmp'])

    if cfg['settings_orig'] is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = cfg['settings_orig']
    else:
        os.environ.pop('DJANGO_SETTINGS_MODULE')


class Test002Integrator(unittest.TestCase):
    def test_000(self):
        cfg = _setup()
        import django_integrator.main

        key = 'INSTALLED_APPS'
        one = django_integrator.main._IMPORTER.settings['TARGET'][key][::]
        django_integrator.add_application(cfg['django_app_name'])
        two = django_integrator.main._IMPORTER.settings['TARGET'][key][::]
        self.assertNotEqual(one, two)
        #
        django_integrator.main._IMPORTER.restore(key)
        nil = django_integrator.main._IMPORTER.settings['TARGET'][key][::]
        self.assertNotEqual(two, nil)
        #
        tmp = list()
        django_integrator.main.add_urlpatterns(tmp)
        self.assertTrue(len(tmp) > 0)
        #
        django_integrator.add_settings(cfg['django_app_name'] + '.settings')

        _teardown(cfg)

    def test_001_list_merge(self):
        "test the list merge function."
        source = ['4', '5', '6']
        target = ['1', '2', '3']
        expect = target[::] + source[::]

        import django_integrator.main
        django_integrator.main._merger_list(source, target)
        self.assertEqual(expect, target)

    def test_002_list_merge_insert(self):
        "test list merge for inserting."
        source = ['nil', 'one', 'last']
        target = ['first', 'one', 'two']
        expect = ['first', 'nil', 'one', 'two', 'last']

        import django_integrator.main
        django_integrator.main._merger_list(source, target)
        self.assertEqual(expect, target)

    def test_003_dict_merge(self):
        "test list merge for inserting."
        source = {'one':1}
        target = {'two':2}
        expect = {'one':1, 'two':2}

        import django_integrator.main
        django_integrator.main.merger(source, target)
        self.assertEqual(expect, target)

    def test_004_unmergable(self):
        "test if we get an exception."
        import django_integrator.main
        self.assertRaises(NotImplementedError, django_integrator.main.merger,
                          int(), list())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
