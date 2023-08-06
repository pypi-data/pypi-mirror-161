import numpy
from setuptools import setup
from Cython.Build import cythonize

setup(
    name = "cross",
    ext_modules = cythonize('cross.pyx'),
	include_dirs=[numpy.get_include()],
)
# python setup.py build_ext --inplace