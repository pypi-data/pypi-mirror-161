<https://python-packaging.readthedocs.io/en/latest/minimal.html>

To install from local:
$ pip install -e .

To install create tar.gz in dist directory:
$ python3 setup.py register sdist

To upload to pypi:
$ twine upload dist/damescraping-0.1.tar.gz
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*

You can install from Internet in a python virtual environment to check:
$ python3 -m venv /tmp/funny
$ cd /tmp/funny
$ source bin/activate
$ pip3 install damescraping

If you upload various tar.gz to pypi, you can need remove old files in dist directory and repeat the process:
$ rm dist/\*tar.gz
$ python3 setup.py register sdist
$ twine upload dist/damescraping-0.1.tar.gz