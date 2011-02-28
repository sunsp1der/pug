from distutils.dir_util import remove_tree

from setuptools import setup, find_packages
import ez_setup
ez_setup.use_setuptools()

try:
    remove_tree('build')
except:
    pass

setup(name='pig',
      description='Python Inventor Gizmo',
      url='http://code.google.com/p/pug',
      author_email='sunsp1der@yahoo.com',
      author='Ivan Spider DelSol',
      maintainer = "Ivan DelSol",
      maintainer_email = "sunsp1der@yahoo.com",
      version='0.9.3',
      license='GNUv3',
      keywords='runtime 2d engine game editor tools development introspective'+\
                ' gui wx',
      packages=find_packages( exclude=['mygame', 'pug', 'pug.*',
                                       'Pig_Demo.*','Pig_Demo']),                                       
      include_package_data = True,
      package_data = {'pig':['editor/Images/*.jpg', 
                             'editor/Images/*.png', 
                             'editor/Images/*.ico',
                             'editor/New_Project/art/*.jpg',
                             'editor/New_Project/art/*.png',
                             'editor/New_Project/art/*.ico',
                             'editor/New_Project/art/*.ttf',
                             ]},
      install_requires = ("wxPython>=2.8.9.2",
                          "pygame>=1.9.1",
                          "NumPy>=1.5.1",
                          "Opioid2D>=6.4")
      )
