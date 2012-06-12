#!/bin/bash

# Push to PyPi
./setup.py sdist upload

# Tag in Git
git push origin master
git push --tags