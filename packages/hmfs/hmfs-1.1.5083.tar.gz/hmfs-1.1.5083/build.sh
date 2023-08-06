sh ./commit.sh
rm -rf dist
rm -rf hamuna_filesystem.egg-info
python setup.py sdist
twine upload ./dist/*