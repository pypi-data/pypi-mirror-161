import os

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from pathlib import Path
import re

# read version string from __init__py
dir_path = os.path.dirname(os.path.realpath(__file__))
verstrline = open(f"{dir_path}/pynibs/__init__.py", "rt").read()
v_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(v_re, verstrline, re.M)
verstr = mo.group(1)

class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        # check_call(f"{sys.path[0]}{os.sep}postinstall{os.sep}install.py")
        install.run(self)


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='pynibs',
      version=verstr,
      description='A python toolbox to conduct non-invasive brain stimulation experiments (NIBS).',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Konstantin Weise, Ole Numssen',
      author_email='kweise@cbs.mpg.de',
      package_data={'pynibs.pckg': ['biosig/biosig4c++-1.9.5.src_fixed.tar.gz']},
      keywords=['NIBS', 'non-invasive brain stimulation', 'TMS', 'FEM'],
      include_package_data=True,
      project_urls={'Home': 'https://gitlab.gwdg.de/tms-localization/pynibs',
                    'Docs': 'https://pynibs.readthedocs.io/',
                    'Twitter': 'https://www.twitter.com/num_ole',
                    'Download': 'https://pypi.org/project/pynibs/'},

      license='GPL3',
      packages=['pynibs',
                'pynibs.exp',
                'pynibs.models',
                'pynibs.util',
                'pynibs.pckg'],
      install_requires=['dill',
                        'h5py',
                        'lmfit',
                        'matplotlib',
                        'numpy',
                        'nibabel',
                        'pandas',
                        'pygpc',
                        'pyyaml',
                        'scipy',
                        'scikit_learn<=1.0',  # python 3.7
                        'packaging',
                        'lxml',
                        'tables',
                        'tqdm',
                        'pillow',
                        'fslpy',
                        'mkl',
                        'trimesh',
                        'meshio',
                        'fmm3dpy',
                        'tvb_gdist',
                        'ortools<=9.1.9490',
                        'seaborn',
                        'icecream'
                        #'pylab'
                        ],
      setup_requires=[
          'cython>=0.29.30'  # pandas
      ],
      python_requires='>=3.7',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Science/Research',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Software Development :: Build Tools',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9', ],

      zip_safe=False,
      cmdclass={
          'develop': PostDevelopCommand,
          'install': PostInstallCommand,
      }, )
