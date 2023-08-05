rm -rf apip.egg-info
rm -rf dist
git add .
git commit -m "Update"
git push origin main
py -m build
twine upload dist/*