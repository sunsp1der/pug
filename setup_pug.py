import sys
import getopt
from distutils.dir_util import remove_tree

from setuptools import setup, find_packages
import ez_setup
ez_setup.use_setuptools()

remove_tree('build')

setup(name='pug',
      description='Python Universal GUI',
      url='http://code.google.com/p/pug',
      author_email='sunsp1der@yahoo.com',
      author='Ivan Spider DelSol',
      maintainer = "Ivan DelSol",
      maintainer_email = "sunsp1der@yahoo.com",
      version='0.9.3',
      license='GNUv3',
      keywords='runtime editor tools development introspective gui wx',
      packages=find_packages( exclude=['mygame', 'pig', 'pig.*',
                                       'Pig_Demo.*','Pig_Demo']),                                       
      include_package_data = True,
      package_data = {'pug':['Images/*.jpg', 'Images/*.png', 'Images/*.ico']},
      install_requires = ("wxPython>=2.8.9.2")
      )
