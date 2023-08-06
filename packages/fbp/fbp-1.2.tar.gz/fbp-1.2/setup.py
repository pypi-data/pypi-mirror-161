import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='fbp',
    packages=['fbp'],
    version='1.2',
    description='Fast C/C++ Builder written in Python',
    license='MIT',
    url='https://github.com/HIDE810/fbp',
    author='Hidman',
    author_email='hide810dev@gmail.com',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    entry_points={ 'console_scripts': [ 'fbp=fbp.__main__:main' ] }
)
