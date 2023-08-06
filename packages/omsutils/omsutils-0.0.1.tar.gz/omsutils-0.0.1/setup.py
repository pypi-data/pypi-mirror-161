from setuptools import setup, find_packages

setup(
    name='omsutils',
    version='0.0.1',
    author='Johnny Hendricks',
    author_email='johnny.hendricks@orbitalmicro.com',
    package_dir={'omsutils': 'src/omsutils'},
    # packages=['omsutils', 'omsutils.fileio'],
    url='http://pypi.python.org/pypi/PackageName/',
    license='LICENSE',
    description='OMS Utilities',
    long_description=open('README.md').read(),
    install_requires=[
        "pytest",
    ],
    packages=find_packages(),
)
