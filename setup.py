VERSION = '0.1.2'

try: from setuptools import setup, find_packages
except ImportError: from distutils.core import setup, find_packages

SETUP_CONF = \
dict (name = "encapsule",
      description = "POSIX application security.",
      download_url = "",

      license = "None",
      platforms = ['OS-independent', 'Many'],

      include_package_data = True,

      keywords = [],

      classifiers = ['Development Status :: 1 - Planning',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Information Technology',
                     'Intended Audience :: System Administrators',
                     'License :: Other/Proprietary License',
                     'Operating System :: POSIX',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.9',
                     'Topic :: System :: Operating System Kernels',
                     'Topic :: System :: Operating System',
                     'Topic :: System :: Systems Administration'])

SETUP_CONF['version'] = VERSION
SETUP_CONF['url'] = 'https://github.com/matrixApi/encapsule'

SETUP_CONF['author'] = ''
SETUP_CONF['author_email'] = ''

SETUP_CONF['long_description'] = ''
SETUP_CONF['packages'] = find_packages()

setup(**SETUP_CONF)
