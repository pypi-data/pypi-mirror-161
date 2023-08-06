# kira-ml-library
Version 0.1.0

## TODO:

1. Choose license for library
2. Add more models

## To test:
1. Ensure that you have Python 3.6+ running on your system
1. Clone / pull this repository
1. In the main directory of the repository, run the following commands:
   ```
   % python3 -m venv venv
   % source venv/bin/activate
   % pip3 install build wheel
   % python3 -m build
   % yes | pip3 uninstall kiraML && pip3 install dist/kiraML-$(cat kiraML/_version.py | cut -d\" -f2)-py3-none-any.whl
   ```
1. Run the suite of tests:
   ```
   % python3 setup.py pytest
   ```
1. Run the example regression program:
   ```
   python3 examples/regression-example.py
   ```  

If the regression program works, you should see a the following diagram:

<img src="images/regression-fig.png" alt="regression diagram" width="50%">

## To build for pip:

```
python3 -m build --sdist
python3 -m build --wheel
twine check dist/*
twine upload dist/*
```
