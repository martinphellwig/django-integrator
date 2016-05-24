"""
Creates a django_integrator compliant project.
"""
import os
import stat
import shutil
import sys
import time
import tempfile
import datetime
from django.core.management.commands import startproject

TEMPLATES = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(TEMPLATES, 'templates')


def _create_project(folder):
    "create the project"
    command = startproject.Command()
    options = {'pythonpath': None, 'name': 'interface', 'directory': folder,
               'files': [], 'verbosity': 1, 'extensions': ['py'],
               'no_color': False, 'traceback': False, 'settings': None,
               'template': None}

    command.handle(**options)

def _create_application(folder, name):
    "create the application in the project."
    cmd = [sys.executable, os.path.join(folder, 'manage.py'), 'startapp', name]
    os.popen(' '.join(cmd))


def _create_folders(directory):
    "create folders"
    folders = ['documentation', 'models', 'tools', 'tests', 'views',
               os.path.join('management', 'commands'),]
    while not os.path.exists(directory):
        time.sleep(0.1)

    for folder in folders:
        os.makedirs(os.path.join(directory, folder))

def _copy_files(directory):
    "copy template files"
    to_copy = [['admin_py.txt', 'admin.py'],
               ['init_py.txt', '__init__.py'],
               ['settings_py.txt', 'settings.py'],
               ['signals_py.txt', 'signals.py'],
               ['urls_py.txt', 'urls.py',],
               ['views_py.txt', 'views.py']]

    for source, target in to_copy:
        source = source = os.path.join(TEMPLATES, source)
        target = os.path.join(directory, target)
        if os.path.exists(target):
            os.remove(target)
        shutil.copy(source, target)

def _move_inits(directory):
    "move modules that have the same name as the folder as an init to that dir."
    items = os.listdir(directory)
    for item in items:
        if item.lower().endswith('.py'):
            part = item[:-3].lower()
            if part in items:
                source = os.path.join(directory, item)
                target = os.path.join(directory, part, '__init__.py')
                os.rename(source, target)

def _make_inits_commands(directory):
    "make the inits in the commands folder"
    items = [['management'], ['management', 'commands']]
    for row in items:
        row.insert(0, directory)
        row.append('__init__.py')
        with open(os.path.join(*row), 'w'):
            pass

def _make_contents_tools(directory):
    "create the init and models module in the tools directory"
    with open(os.path.join(directory, 'tools', '__init__.py'), 'w'):
        pass

    source = os.path.join(TEMPLATES, 'models_py.txt')
    target = os.path.join(directory, 'tools', 'models.py')
    shutil.copy(source, target)


def _create_requirements(directory):
    "Create the various requirements.txt files"
    # application requirements
    with open(os.path.join(directory, 'requirements.txt'), 'w') as file_write:
        file_write.write('django\n')

    # interface requirements
    with open(os.path.join('interface', 'requirements.txt'), 'w') as file_write:
        file_write.write('Django\ncoverage<4.0.0\npylint\nipython\n')
        file_write.write('django-integrator\n')

    # development requirements
    with open('requirements.txt', 'w') as file_write:
        file_write.write('-r interface/requirements.txt\n')
        file_write.write('-r application/requirements.txt\n')

def _copy_into_project():
    "Copy the files into the projects root."
    to_copy = [['README.txt', 'README.txt'],
               ['setup.cfg', 'setup.cfg']]

    for source, target in to_copy:
        source = source = os.path.join(TEMPLATES, source)
        target = os.path.join(target)
        shutil.copy(source, target)

def _append_interface_settings(name):
    "Append to interface settings"
    with open(os.path.join('interface', 'settings.py'), 'a') as file_append:
        file_append.write('\n# Import applications\n')
        file_append.write('# pylint:disable=wrong-import-position\n')
        file_append.write('import django_integrator\n')
        text = "django_integrator.add_application('%s')\n" % name
        file_append.write(text)

def _append_interface_urls():
    "Append to interface settings"
    with open(os.path.join('interface', 'urls.py'), 'a') as file_append:
        file_append.write('\n# Import applications\n')
        file_append.write('# pylint:disable=wrong-import-position\n')
        file_append.write('import django_integrator\n')
        file_append.write('django_integrator.add_urlpatterns(urlpatterns)')

def _write_developer_reset(name):
    "write the developer reset."
    read_name = 'developer_reset_py.txt'
    write_name = 'developer_reset.py'
    with open(os.path.join(TEMPLATES, read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        text = text.format(name=name)
        with open(write_name, 'w') as file_write:
            file_write.write(text)

    os.chmod(write_name, stat.S_IEXEC)

def _write_license(author, email):
    "Write the license file"
    read_name = 'license_template.txt'
    write_name = 'LICENSE.txt'
    year = datetime.datetime.now().strftime('%Y')
    with open(os.path.join(TEMPLATES, read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        text = text.format(author=author, email=email, year=year)
        with open(write_name, 'w') as file_write:
            file_write.write(text)

def _write_info(class_name, name, verbose):
    "Write the info file."
    read_name = 'info_py.txt'
    write_name = os.path.join(name, '__info__.py')
    with open(os.path.join(TEMPLATES, read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        kwargs = {'class':class_name, 'name':name, 'verbose':verbose}
        text = text.format(**kwargs)
        with open(write_name, 'w') as file_write:
            file_write.write(text)

def _write_setup(kwargs):
    "Write the setup file."
    read_name = 'setup_py.txt'
    write_name = 'setup.py'
    with open(os.path.join(TEMPLATES, read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        text = text.format(**kwargs)
        with open(write_name, 'w') as file_write:
            file_write.write(text)


def main(configuration):
    "main functionality"
    cwd_original = os.path.abspath(os.getcwd())
    folder = tempfile.mkdtemp(prefix='di_stage_')
    os.chdir(folder)

    _create_project(folder)
    _create_application(folder, configuration['name'])
    _create_folders(configuration['name'])
    _copy_files(configuration['name'])
    _move_inits(configuration['name'])
    _make_inits_commands(configuration['name'])
    _make_contents_tools(configuration['name'])
    _create_requirements(configuration['name'])
    _copy_into_project()
    _append_interface_settings(configuration['name'])
    _append_interface_urls()
    _write_developer_reset(configuration['name'])
    _write_license(configuration['author'], configuration['email'])
    _write_info(configuration['class'], configuration['name'],
                configuration['verbose'])
    _write_setup(configuration)
    os.chdir(cwd_original)

# if __name__ == '__main__':
#     tmp = {'name':'django_test',
#            'class':'DjangoTest',
#            'verbose':'Django test application',
#            'author':'Martin P. Hellwig',
#            'email':'martin.hellwig@gmail.com'}
#     main(tmp)