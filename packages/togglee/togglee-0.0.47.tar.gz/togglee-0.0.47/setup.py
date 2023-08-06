import os
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('requirements_prod.txt') as f:
    required = f.read().splitlines()

version = '0.0.' + os.getenv("GITHUB_RUN_NUMBER", "1-SNAPSHOT")

setup(
    name='togglee',
    version=version,
    description='Simple toggles for python from a url reference',
    long_description=readme,
    long_description_content_type= 'text/x-rst',
    author='kanekotic',
    author_email='me@kanekotic.com',
    url='https://github.com/togglee/togglee-python',
    install_requires=required,
    license='Apache-2.0',
    packages=find_packages(where='src'),
    package_dir={
        '': 'src',
    }
)
