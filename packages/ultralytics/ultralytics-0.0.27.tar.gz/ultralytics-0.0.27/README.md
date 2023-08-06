[![codecov](https://codecov.io/gh/ultralytics/package-framework/branch/master/graph/badge.svg?token=YWaAfJ18gg)](https://codecov.io/gh/ultralytics/package-framework)
<a href="https://github.com/ultralytics/hub-pip-package/actions/workflows/ci.yaml"><img src="https://github.com/ultralytics/hub-pip-package/actions/workflows/ci.yaml/badge.svg" alt="CI CPU"></a>

# package framework

## Installation

```console
# clone project repository
git clone git@github.com:ultralytics/package-framework.git
# navigate to project root directory
cd package-framework
# create python virtual environment and activate it (optional)
virtualenv venv
source venv/bin/activate
# install project
python setup.py install
```

# Deployment

## Requirements

Python 3.8 or later with all [requirements.txt](https://github.com/ultralytics/pip/blob/master/requirements.txt)
dependencies installed, including `build` and `twine`.
```bash
python -m pip install -U pip
pip install -U build twine
```

## Pip Package Steps

Deploy from master branch ⚠

### https://pypi.org/

```bash
# Build and upload https://pypi.org/
rm -rf build dist && python -m build && python -m twine upload dist/*
# username: __token__
# password: pypi-AgENdGVzdC5weXBpLm9yZ...

# Download and install
pip install -U ultralytics

# Import and test
python -c "from ultralytics import simple; print(simple.add_one(10))"
sample_script
```

### https://test.pypi.org/

```bash
# Build and upload https://test.pypi.org/
rm -rf build dist && python -m build && python -m twine upload --repository testpypi dist/*
# username: __token__
# password: pypi-AgENdGVzdC5weXBpLm9yZ...

# Download and install
pip install -U --index-url https://test.pypi.org/simple/ --no-deps ultralytics2==0.0.9

# Import and test
python -c "from ultralytics import simple; print(simple.add_one(10))"
sample_script
```

### Test HUB training

```python
from src import ultralytics

ultralytics.checks()
ultralytics.start('API_KEY')
```
