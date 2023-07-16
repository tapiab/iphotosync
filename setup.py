from setuptools import setup, find_packages

entry_points = {
    'console_scripts': [
        'piephone=piephone.app:main',
    ],
}

setup(
    name='piephone',
    version='0.5.0',
    packages=find_packages(),
    maintainer='benoit.tapia@sidhes.com',
    description='Synchronize iPhone photo',
    install_requires=[line for line in open('requirements.txt')]
)

