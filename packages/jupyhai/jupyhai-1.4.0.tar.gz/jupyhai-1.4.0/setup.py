"""
jupyhai setup
"""
import json
import sys
from pathlib import Path

import setuptools

HERE = Path(__file__).parent.resolve()

# The name of the project
name = "jupyhai"

jupyhai_path = (HERE / name.replace("-", "_"))
labextension_path = (jupyhai_path / "labextension")
nbextension_path = (jupyhai_path / "nbextension")

# Representative files that should exist after a successful build
ensured_targets = [
    str(labextension_path / "package.json"),
    str(labextension_path / "static/style.js"),
    str(nbextension_path / "jupyhai.js"),
]

labext_name = "jupyhai"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, str(labextension_path.relative_to(HERE)), "**"),
    ("share/jupyter/labextensions/%s" % labext_name, str("."), "install.json"),
    ("etc/jupyter/jupyter_server_config.d",
     "jupyter-config/server-config", "jupyhai.json"),
    # For backward compatibility with notebook server
    ("etc/jupyter/jupyter_notebook_config.d",
     "jupyter-config/nb-config", "jupyhai.json"),
]

long_description = (HERE / "README.md").read_text()

# Get the package info from package.json
pkg_json = json.loads((HERE / "package.json").read_bytes())
version = pkg_json["version"].replace("-alpha.", "a").replace("-beta.", "b").replace("-rc.", "rc")

requirements = [
    'jupyter_server>=1.6,<2',
    'notebook>=6.0',  # (required by jupyterhub anyway)
    'valohai-cli>=0.21.0',
    'valohai-yaml>=0.23.0',
    'valohai-utils>=0.2.0',
    'aiohttp~=3.7.0',
]

test_requirements = [
    'pytest==5.1.1',
    'pytest-cov==2.7.1',
]

setup_args = dict(
    name=name,
    version=version,
    url=pkg_json["homepage"],
    author=pkg_json["author"]["name"],
    author_email=pkg_json["author"]["email"],
    description=pkg_json["description"],
    license=pkg_json["license"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include=('jupyhai*',)),
    install_requires=requirements,
    tests_require=test_requirements,
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    entry_points={
        'console_scripts': [
            'jupyhai = jupyhai.cli.__main__:main',
        ],
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Framework :: Jupyter :: JupyterLab :: 3",
        "Framework :: Jupyter :: JupyterLab :: Extensions",
        "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
    ],
)

try:
    from jupyter_packaging import get_data_files, npm_builder, wrap_installers

    post_develop = npm_builder(build_cmd="build:prod", source_dir="src", build_dir=jupyhai_path)
    setup_args["cmdclass"] = wrap_installers(post_develop=post_develop, ensured_targets=ensured_targets)
    setup_args["data_files"] = get_data_files(data_files_spec)
except ImportError as e:
    import logging

    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.warning("Build tool `jupyter-packaging` is missing. Install it with pip or conda.")
    if not ("--name" in sys.argv or "--version" in sys.argv):
        raise e

if __name__ == "__main__":
    setuptools.setup(**setup_args)
