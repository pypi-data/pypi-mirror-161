from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

VERSION = '1.0.1'
DESCRIPTION = 'Fast and reliable way to analize geospatial data.'
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="geotoolsconnector",
    version=VERSION,
    author="Sanil Safić",
    author_email="<safic.sanil@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['flask', 'requests', 'asyncio'],
    keywords=['python', 'GeoTools', 'Geospatial analysis', 'Web Service', 'Geospatial data', 'Pipe request', 'GeoPandas', 'QGIS', 'PostGIS'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)