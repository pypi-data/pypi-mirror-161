import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='fbp',
    packages=['fbp'],
    version='1.3.4',
    description='Fast C/C++ Builder written in Python',
    license='MIT',
    url='https://github.com/bomkei/BuildPy',
    author='bomkei',
    author_email='bunkeiprogrammer@gmail.com',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    entry_points={ 'console_scripts': [ 'fbp=fbp.__main__:main' ] }
)
