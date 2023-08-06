import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oatlib",
    version="0.0.7rc4",
    author="Massimiliano Cannata",
    author_email="massimiliano.cannata@gmail.com",
    description="Observation Analysis Tool: library to handle time series",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/ist-supsi/OAT",
    packages=setuptools.find_packages(),
    install_requires=[
        'datetime','dateutils','pandas','numpy','scipy',
        'requests','spatialite','isodate'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.8',
)

# install_requires=[
#         'datetime','dateutil','osgeo','pandas','numpy','scipy'
#         'requests','StringIO','os','io','pyspatialite','copy','isodate',
#         '__future__','json','math','calendar'
#     ]

# packages=setuptools.find_packages(),