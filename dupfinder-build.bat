@echo off
rmdir /s /q build dist dupfinder.egg-info
python setup.py sdist bdist_wheel