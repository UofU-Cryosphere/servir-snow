from setuptools import setup

setup(
    name='snow-rs',
    version='0.1',
    packages=['snowrs', 'snowrs.amsr2'],
    url='https://github.com/UofU-Cryosphere/servir-snow',
    author='Joachim Meyer',
    author_email='j.meyer@utah.edu',
    description='Library to process MODIS tiles',
    install_requires=[
        'click', 'beautifulsoup4', 'gdal', 'numpy',  'pyproj', 'requests'
    ]
)
