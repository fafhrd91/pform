import os
import sys
from setuptools import setup, find_packages

version = '0.2'

install_requires = ['setuptools',
                    'pyramid >= 1.4a2',
                    'pyramid_jinja2',
                    'player >= 0.3',
                    'pytz',
                    ]

if sys.version_info[:2] == (2, 6):
    install_requires.extend((
            'argparse',
            'ordereddict',
            'unittest2'))

if sys.version_info[:2] in ((2,6),(2,7)):
    install_requires.extend(('simplejson',))

tests_require = install_requires + ['nose', 'mock']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(name='pform',
      version=version,
      description=('Form generation library for pyramid'),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: Implementation :: CPython",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='https://github.com/fafhrd91/pform/',
      license='BSD',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require = dict(test=tests_require),
      tests_require=tests_require,
      test_suite='nose.collector',
      include_package_data=True,
      zip_safe=False,
      message_extractors={'pform': [
          ('scripts/**', 'ignore', None),
          ('static/**', 'ignore', None),
          ('tests/**', 'ignore', None),
          ('*/tests/**', 'ignore', None),
          ('**.py', 'lingua_python', None),
          ('**.pt', 'lingua_xml', None),
          ('**.mustache', 'mustache', None),
          ('**.hb', 'mustache', None),
          ]},
      )
