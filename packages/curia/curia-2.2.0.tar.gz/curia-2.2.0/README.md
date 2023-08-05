[![PyPI version](https://badge.fury.io/py/curia.svg)](https://badge.fury.io/py/curia)

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=FoundryAI_curia-python-sdk&metric=alert_status&token=d5fecb91736894944e664dc8dcc119d19c73990a)](https://sonarcloud.io/dashboard?id=FoundryAI_curia-python-sdk)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=FoundryAI_curia-python-sdk&metric=bugs&token=d5fecb91736894944e664dc8dcc119d19c73990a)](https://sonarcloud.io/dashboard?id=FoundryAI_curia-python-sdk)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=FoundryAI_curia-python-sdk&metric=coverage&token=d5fecb91736894944e664dc8dcc119d19c73990a)](https://sonarcloud.io/dashboard?id=FoundryAI_curia-python-sdk)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=FoundryAI_curia-python-sdk&metric=sqale_rating&token=d5fecb91736894944e664dc8dcc119d19c73990a)](https://sonarcloud.io/dashboard?id=FoundryAI_curia-python-sdk)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=FoundryAI_curia-python-sdk&metric=reliability_rating&token=d5fecb91736894944e664dc8dcc119d19c73990a)](https://sonarcloud.io/dashboard?id=FoundryAI_curia-python-sdk)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=FoundryAI_curia-python-sdk&metric=security_rating&token=d5fecb91736894944e664dc8dcc119d19c73990a)](https://sonarcloud.io/dashboard?id=FoundryAI_curia-python-sdk)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=FoundryAI_curia-python-sdk&metric=vulnerabilities&token=d5fecb91736894944e664dc8dcc119d19c73990a)](https://sonarcloud.io/dashboard?id=FoundryAI_curia-python-sdk)

![Release](https://github.com/FoundryAI/curia-python-sdk/workflows/Release%20Workflow/badge.svg)

# Curia Python SDK
Curia Python SDK is a library for training and using risk and impactability models on Curia.

For detailed documentation, including the API reference, see our docs at https://foundryai.github.io/curia-python-sdk/.

### Installing the Curia Python SDK
The Curia Python SDK is built to PyPi and can be installed with `pip` as follows: 
```
pip install curia
```

You can install from source by cloning this repository and running a pip install command in the root directory of the repository:
```
git clone https://github.com/FoundryAI/curia-python-sdk.git
cd curia-python-sdk
pip install .
```

##### Supported Operating Systems
Curia Python SDK supports Unix/Linux and Mac.

##### Supported Python Versions
Curia Python SDK is tested on:
- Python 3.8

##### Curia Permissions
Curia Python SDK will utilize the Curia Platform when training models and generating predictions. 
You will need access to the platform with appropriate permissions to fully utilize the SDK.

##### Running tests
Curia Python SDK has unit tests.
To run the tests:
```
python setup.py pytest
```

##### Building Sphinx docs
Curia Python SDK has Sphinx docs.
To build the docs, run:
```
cd doc
make html
```

To preview the site with a Python web server:
```
cd docs/_build/html
python -m http.server 8000
```
View the docs by visiting http://localhost:8080

### Curia API Token
To use the Curia Python SDK you will need a Curia API Token. To access your API Token visit https://app.curia.ai/settings.

### Use gnu-sed
Visit https://medium.com/@bramblexu/install-gnu-sed-on-mac-os-and-set-it-as-default-7c17ef1b8f64 to see how to install gnu-sed for consistency in fixing swagger imports
```export PATH="/usr/local/opt/gnu-sed/libexec/gnubin:$PATH"```

### Using the Curia Python SDK
```python
from curia.session import Session
from curia.risk import RiskModel
from curia.synthetic_data import generate_data

# Create synthetic data (demo/testing purposes only)
(X_train, X_test, _, _, y_train, y_test, _, _, _, _) = generate_data(binary_outcome=True)

# Create a session
curia_session = Session(api_token="YOUR_API_TOKEN")

# Instantiate a model
model = RiskModel(
    session=curia_session, 
    name="your-model-name",
    project_id="YOUR_PROJECT_ID",
    environment_id="YOUR ENVIRONMENT_ID"
)

# Train a model on the Curia Platform
model.train(features=X_train, label=y_train)

# Get predictions from your model on the Curia Platform
predictions = model.predict(features=X_test)
```

## Cut your own release (not recommended)
Sometimes we may have updates that are currently in the development environment, 
but not accessible in production yet.  When this happens, the SDK will not reflect
the latest changes in develop.  To be able to use new features of the API, you can
cut a new release of the SDK and use the latest version.  

*BE CAREFUL - MAKE SURE YOU KNOW WHY YOU ARE DOING THIS* 

To cut a new release based on the Dev API, run `make build-api-dev`.  In order 
to get some sed commands to work on Mac, you may need to install and use 
[Gnu-Sed](#use-gnu-sed)

First, update the version in `src/curia/__init__.py`
Then build the source distribution: `python setup.py sdist bdist_wheel`
Finally, upload the new distribution to pypi: `python -m twine upload dist/*`
You will be prompted for a username and password.  
- Your username is `__token__`
- Your password is stored in 1Password in the Curia vault in the `PyPi Curia Project` secure document

