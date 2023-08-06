from setuptools import setup, find_packages

setup(name = 'Ir_calculator',
version = '0.3',
description= 'Calculate Criminla IR',
author= 'Jay Jo',
install_requires = ['numpy', 'pandas', 'numpy_financial','pyxirr'],
packages=find_packages(), #name of the Directory
zip_safe =False)
