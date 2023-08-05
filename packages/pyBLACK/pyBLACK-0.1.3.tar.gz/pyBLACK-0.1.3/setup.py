from __future__ import print_function
import pip
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup
from pyblack import __version__

print('Checking Cython')
try:
    import Cython
    cyv=Cython.__version__
    print("OK! (Version: %s"%cyv)
except:
    print("Cython is not present, I will install it for you, my lord")
    pip.main(['install','Cython'])




setup(
    name='pyBLACK',
    version=__version__,
    author='G. Iorio',
    author_email='giuliano.iorio.astro@gmail.com',
    packages=['pyblack','pyblack/gw'],
    scripts=[],
    url='https://gitlab.com/iogiul/pyblack',
    license='',
    description='suit of utilities for the DEMOBLACK group',
    long_description=open('README.rst').read(),
    install_requires=[
      "numpy", "scipy>1.4"
    ],
    include_package_data=True,
)
