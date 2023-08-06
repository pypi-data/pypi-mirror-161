from setuptools import setup, find_packages
import os

__version__ = os.environ["VERSION"].split('/')[-1][1:]
print("get version", __version__)

setup(
    name='fstats',
    version=__version__,
    author="bbing",
    install_requires=['psutil'],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fstats = fstats.__main__:main'
        ]
    }
)
