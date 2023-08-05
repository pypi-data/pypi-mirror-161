import codecs
import os.path
from glob import glob

from sphinx.setup_command import BuildDoc

cmdclass = {'build_sphinx': BuildDoc}

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

    raise RuntimeError("Unable to find version string.")

setup_packages = [
    'Cython',
    'pytest-runner'
]

required_packages = [
    'importlib-metadata<4',
    'ipykernel',
    'numpy==1.21',
    'scipy==1.7.3',
    'pandas==1.3.5',
    'requests',
    'dynaconf',
    'validation_decorators',
    'scikit-learn',
    'logzero',
    'docutils',
    'importlib-metadata<4',
    'packaging',
    'pymaybe',
    'boto3',
    'pyarrow',
    'requests'
]

test_packages = [
    'click',
    'freezegun',
    'moto',
]

extras = {
    'testing': {
        'pytest-cov',
        'pytest-pylint',
        'pytest-mock',
        'flake8',
    },
    'docs': {
        'sphinx',
        'sphinx_rtd_theme',
        'sphinxcontrib-apidoc'
    }
}

name = "curia"
version = get_version("src/curia/__init__.py")

setup(
    name=name,
    version=version,
    description="A library for training and using risk & impactability models on Curia",
    packages=find_packages("src"),
    package_dir={
        "": "src",
        # 'curia': 'src/curia',
        'curia.api': 'src/curia/api',
        'swagger_client': 'src/curia/api/swagger_client'
    },
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    long_description=readme(),
    long_description_content_type='text/markdown',
    author="Curia.ai",
    url="https://github.com/FoundryAI/curia-python-sdk",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    setup_requires=setup_packages,
    install_requires=required_packages,
    tests_require=test_packages,
    extras_require=extras,
    cmdclass=cmdclass,
    # these are optional and override conf.py settings
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'source_dir': ('setup.py', 'doc'),
            'build_dir': ('setup.py', 'doc/_build')
        }
    },
)
