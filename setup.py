from setuptools import setup, find_packages

setup(
    name='iPhonePhotoSync',
    version='0.3.0',
    packages=find_packages(),
    maintainer='benoit.tapia@free.fr',
    description='Sycnhronize iPhone photo',
    install_requires=[line for line in open('requirements.txt')]
)

