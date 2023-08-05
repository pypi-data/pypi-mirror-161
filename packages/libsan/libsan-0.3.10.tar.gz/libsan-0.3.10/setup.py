from __future__ import absolute_import, division, print_function, unicode_literals
from setuptools import setup, find_packages
from distutils.util import convert_path

install_requires = ['python-augeas', 'future', 'six', 'distro', 'netifaces', 'ipaddress', 'requests']
setup_requires = ['pytest-runner']
extras_require = {'ssh': ["ssh2-python"]}

main_ns = {}
ver_path = convert_path('libsan/_version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(name='libsan',
      description='Python modules to manage SAN devices',
      version=main_ns['__version__'],
      license='GPLv3+ (see LICENSE)',
      packages=find_packages(exclude=['bin', 'tests']),
      # packages=['libsan', 'libsan/host', 'libsan/switch', 'libsan/switch/cisco',
      #           'libsan/switch/brocade', 'libsan/physwitch', 'libsan/physwitch/apcon',
      #           'libsan/array', 'libsan/misc', 'libsan/array/dell',
      #           'libsan/array/linux', 'libsan/array/netapp', 'libsan/array/emc'],
      install_requires=install_requires,
      setup_requires=setup_requires,
      extras_require=extras_require,
      dependency_links=['https://github.com/PythonCharmers/python-future/archive/master.zip?ref=master#egg=future',
                        'https://github.com/nir0s/distro/archive/master.tar.gz?ref=master#egg=distro'],
      # data_files=[('/etc', ['sample_san_top.conf'])],
      scripts=['bin/sancli'],
      tests_require=['pytest'],
      test_suite='tests',
      url='https://gitlab.com/rh-kernel-stqe/python-libsan.git',
      author='Bruno Goncalves',
      author_email='bgoncalv@redhat.com',
      # long_description=open("README.md").read()
      )
