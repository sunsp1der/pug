from setuptools import setup, find_packages

setup(name='Pig_Pug',
      description='Python Inventor Gizmo and Python Universal GUI',
      url='http://code.google.com/p/pug',
      author_email='sunsp1der@yahoo.com',
      author='Ivan Spider DelSol',
      version='0.8.2',
      packages=find_packages( exclude=['mygame']),
      package_dir={'pig': 'pig', 'pug': 'pug'},
      package_data={'pig.editor': ['editor/Images/*.*']},
      )
