from distutils.dir_util import remove_tree
from distutils.core import setup
#import ez_setup
#ez_setup.use_setuptools()
#from setuptools import setup, find_packages

try:
    remove_tree('build')
except:
    pass

setup(name='pig',
      scripts = ['post_install.py'],
      description='Python Inventor Gizmo',
      long_description=
"""A python based graphical editor for creating games and art.
Requirements: wxPython, pygame, NumPy, Opioid2D.
""",
      url='http://code.google.com/p/pug',
      author_email='sunsp1der@yahoo.com',
      author='Ivan Spider DelSol',
      maintainer = "Ivan DelSol",
      maintainer_email = "sunsp1der@yahoo.com",
      version='0.9.3',
      license='GNUv3',
      keywords='runtime 2d engine game editor tools development introspective'+\
                ' gui wx',
      packages=['pig',
                'pig.actions',
                'pig.components',
                'pig.components.behavior',
                'pig.components.collision',
                'pig.components.controls',
                'pig.components.gameplay',
                'pig.components.gui',
                'pig.components.scene',
                'pig.components.sound',
                'pig.components.spawn',
                'pig.editor',
                'pig.editor.agui',
                'pig.editor.New_Project',
                'pig.editor.New_Project.components',
                'pig.editor.New_Project.objects',
                'pig.editor.New_Project.scenes',
                'pig.editor.Pig_Demo',
                'pig.editor.Pig_Demo.components',
                'pig.editor.Pig_Demo.objects',
                'pig.editor.Pig_Demo.scenes',
                'pig.editor.wm_ext'
                ],
      package_data = {'pig':['readme.txt',
                             'editor/Images/*.jpg', 
                             'editor/Images/*.png', 
                             'editor/Images/*.ico',
                             'editor/New_Project/art/*.jpg',
                             'editor/New_Project/art/*.png',
                             'editor/New_Project/art/*.ico',
                             'editor/New_Project/art/*.ttf',
                             'editor/New_Project/sound/*.wav',
                             'editor/New_Project/sound/*.mp3',
                             'editor/Pig_Demo/art/*.jpg',
                             'editor/Pig_Demo/art/*.png',
                             'editor/Pig_Demo/art/*.ico',
                             'editor/Pig_Demo/art/*.ttf',
                             'editor/Pig_Demo/art/explosion/*.png',
                             'editor/Pig_Demo/sound/*.wav',
                             'editor/Pig_Demo/sound/*.mp3',
                             ]},
      requires = ("wxPython (>=2.8.9, <2.9)",
                          "pygame (>=1.9.1)",
                          "NumPy (>=1.5.1)",
                          "Opioid2D (>=0.6.5)")
                             
      )
