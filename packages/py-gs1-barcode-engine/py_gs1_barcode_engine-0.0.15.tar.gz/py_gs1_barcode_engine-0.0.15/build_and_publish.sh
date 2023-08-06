set -ex

rm -rf dist
# python -m build  # build both
python -m build -s   # build sdist only
python -m twine upload --verbose dist/* --username stolmen
