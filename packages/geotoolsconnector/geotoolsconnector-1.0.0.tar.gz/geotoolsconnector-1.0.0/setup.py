from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'Fast and reliable way to analize geospatial data.'

# Setting up
setup(
    name="geotoolsconnector",
    version=VERSION,
    author="Sanil Safić",
    author_email="<safic.sanil@gmail.com>",
    description=DESCRIPTION,
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