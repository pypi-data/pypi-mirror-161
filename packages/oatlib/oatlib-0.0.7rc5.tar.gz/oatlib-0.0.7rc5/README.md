# OAT (Observation Analysis Tool)


A Python library (oatlib) to manage sensor data in Python.
It provides objects and methods to manipulate 
obeservation time series. It support data loading, export and saving
on different format (CSV, sqlite, istSOS).

- lib documentation: https://ist-supsi.gitlab.io/OAT


## installation

> pip install oatlib

## Create pypi package

python setup.py sdist bdist_wheel
twine upload dist/*

## update library documentation

pdoc3 --force --html -o html_doc  oatlib

## test in a 3.10.5 python
docker run -p 10000:8888 -v /home/maxi/GIT/OAT/oatlib:/home/jovyan/work jupyter/scipy-notebook:807999a41207