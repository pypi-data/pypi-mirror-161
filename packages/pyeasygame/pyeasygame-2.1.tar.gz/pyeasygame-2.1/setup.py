from setuptools import setup

setup(
   name='pyeasygame',
   version='2.1',
   description='A useful game engine for beginners',
   author='Morris El Helou',
   author_email='morriselhelou816@gmail.com',
   packages=['pyeasygame'], 
   install_requires=['pygame','keyboard'], #external packages as dependencies
)