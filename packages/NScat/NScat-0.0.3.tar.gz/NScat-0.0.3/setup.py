from setuptools import setup, find_packages
import codecs
import os

def readfile(filename):
    with open(filename, encoding="utf-8") as fp:
        filecontents = fp.read()
    return filecontents

def check_dependencies():
   install_requires = []
   return install_requires


setup(name='NScat',
version='0.0.3',
description='A package python to query various neutron star parameters from publicly available databases',
      
url='https://nscat.readthedocs.io/en/latest/',
author='Rohit Chinchwadkar, Satyajit ,Chakraborty, Shreetama Pradhan, Aishwarya Panja and Sushan Konar',
author_email='chinchwadkarrohit4@gmail.com',
license='MIT',
packages=find_packages(),
#install_requires=readfile("requirements.txt"),
install_requires=['rich>=10.10.0'],      
include_package_data=True,
#package_data={'home/rohit/Magnetar_catalog/Test_local_4/Test4':['data/MMC1.']}
#zip_safe=False
 )