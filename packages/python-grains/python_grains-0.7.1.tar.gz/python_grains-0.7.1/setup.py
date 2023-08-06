from setuptools import setup, find_packages
from pathlib import Path
import re
import os

PACKAGE_DIR = os.path.join(Path(__file__).resolve().parent, 'python_grains')
with open(os.path.join(PACKAGE_DIR, 'version.py')) as version_file:
    verstrline = version_file.read().strip()

VSRE = r'^__version__ = [\']([0-9\.]*)[\']'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise Exception('No version string found')


with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='python_grains',
    version=VERSION,
    description='Grains of Python',
    license='MIT',
    packages=find_packages(),
    author='Jacob Noordmans',
    author_email='jacob@graindataconsultants.com',
    keywords=['Grain', 'Python']
)

install_requires = [
    'redis',
    'pytz',
    'requests'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)