![Fincloud.io](https://avatars.githubusercontent.com/u/73434302?s=100&v=4)
# ariaclient

This is a python wrapper around the REST api for the multi message-transport ARIA platform.

Build instructions
==================

1. Ensure that the project version number is correctly updated [src/ariaclient/__init__.py](src/ariaclient/__init__.py)

2. `pip install -r requirements_dev.txt`      `python -m build`

3. Then to upload into pyi  `twine upload dist/*`