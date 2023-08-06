"""
Example setup.py from https://github.com/activescott/python-package-example/blob/master/package-project/src/setup.py.
"""
# Always prefer setuptools over distutils
import os
from distutils.command.sdist import sdist

import setuptools

here = os.path.abspath(os.path.dirname(__file__))


def __read_meta(fn):
    with open(os.path.join(here, "energinetml", "meta", fn)) as f:
        return f.read().strip()


def _write_meta(fn, text):
    with open(os.path.join(here, "energinetml", "meta", fn), "w") as f:
        return f.write(text.strip())


class sdist_hg(sdist):
    """Add git short commit hash to version.
    Based on https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/specification.html
    """

    user_options = sdist.user_options + [
        ("dev", None, "Add a dev marker"),
        ("build=", None, "Build number"),
    ]

    def initialize_options(self):
        sdist.initialize_options(self)
        self.dev = None
        self.build = None

    def run(self):
        if self.build:
            if self.build.startswith("+"):
                prefix = ""
            else:
                prefix = "."
            self.distribution.metadata.version += f"{prefix}{self.build}"
            _write_meta("PACKAGE_VERSION", self.distribution.metadata.version)
            print(self.distribution.metadata.version)
        sdist.run(self)


name = __read_meta("PACKAGE_NAME")
version = __read_meta("PACKAGE_VERSION")
python_requires = __read_meta("PYTHON_VERSION")
command = __read_meta("COMMAND_NAME")


setuptools.setup(
    name=name,
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,
    description="Energinet Machine Learning",
    author="Koncern Digitalisering Advanced Analytics Team",
    author_email="mny@energinet.dk, xjakk@energinet.dk",
    # Choose your license
    license="Apache Software License 2.0",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: Apache Software License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        f"Programming Language :: Python :: {python_requires}",
    ],
    # What does your project relate to?
    keywords=[],
    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=setuptools.find_packages(),  # Required
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # TODO SPECIFIC VERSION OF REQUIREMENTS!
    install_requires=[
        "requests",
        "Jinja2==3.0.1",
        "pandas>=1.2.0",
        "packaging==20.9",
        "click==8.0.3",
        "click-spinner==0.1.10",
        "fastapi==0.63.0",
        "uvicorn==0.15.0",
        "pydantic==1.8.1",
        "requirements-parser==0.2.0",
        "azure-cli-core==2.34.1",
        "azure-identity==1.7.0",
        "azureml-core==1.39.0",
        "azureml-dataset-runtime==1.39.0",
        "azure-monitor-opentelemetry-exporter==1.0.0b4",
        "pyopenssl<21.0.0",
        "waitress",
        "flask",
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={"dev": [], "build": [], "test": []},
    cmdclass={"sdist": sdist_hg},
    python_requires=">=3.9.0",
    include_package_data=True,
    package_data={"": ["meta/*", "static/*", "static/model_template/*"]},
    entry_points={"console_scripts": [f"{command}=energinetml.cli:main"]},
)
