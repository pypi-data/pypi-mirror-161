# -*- coding: utf-8 -*-
import sys
import time

from setuptools import setup

from fserver import conf

now = time.strftime('%Y/%m/%d', time.localtime(time.time()))
if conf.BUILD_TIME != now:
    print('conf.BUILD_TIME is invalid: %s != %s' % (conf.BUILD_TIME, now))
    sys.exit(-1)
if conf.DEBUG:
    print('debug mode is open by default')
    sys.exit(-1)

install_requires = ['Flask >= 1.1.2', 'Flask-HTTPAuth >= 4.6.0', 'gevent >= 20.6.2']
try:
    from os import scandir
except ImportError:
    install_requires.append('scandir >= 1.0.0')

home_page = 'https://github.com/Carrotor116/fserver'

with open('README.md', 'r') as fr:
    long_description = fr.read()
    long_description.replace('[MIT](LICENSE)', '[MIT]({}/blob/master/LICENSE)'.format(home_page))

setup(
    name='fserver',
    version=conf.VERSION,
    description='File Sharing Server implemented with flask and gevent',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=home_page,
    author='Nonu',
    author_email='carrotor116@gmail.com',
    license='MIT',
    packages=['fserver'],
    install_requires=install_requires,
    package_data={
        '': ['templates/*.html', 'static/*']
    },
    entry_points={
        'console_scripts': [
            'fserver=fserver.cmd:run_fserver'
        ]
    }
)

# python setup.py sdist bdist_wheel --universal
# twine upload dist/*
