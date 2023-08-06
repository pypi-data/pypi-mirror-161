import setuptools
from setuptools import setup

setup(
   name='fsvpy',
   version='1.0.1',
   description='streak finding module',
   long_description='Efficient algorithm for generalized streak finding for velocimetry applications.',
   author='Michelle Driscoll',
   author_email='michelle.driscoll@northwestern.edu',
   url="",
   packages = setuptools.find_packages(),
   install_requires=['pims', 'matplotlib', 'pandas', 'numpy', 'scikit-image', 'networkx'] #external packages as dependencies
)
