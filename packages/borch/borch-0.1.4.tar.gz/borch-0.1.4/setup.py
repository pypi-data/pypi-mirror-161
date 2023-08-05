"""
borch Setup
===========

NB ``borch/version.py`` is created automatically. Do not manually add a
version file.
"""
import os
import re
import shutil
import subprocess
from glob import glob
from setuptools import setup, find_packages


def readme():
    """Open and read README.md"""
    with open("README.md") as f:
        return f.read()


def get_pytorch_arch():
    "Get the arch to append to the pytorch version"
    arch = os.getenv("ARCH")
    if arch is None:
        return ""
    arch = arch.lower()
    if arch == "cpu":
        return "+cpu"
    if arch == "gpu":
        return ""
    if re.fullmatch(r"^[+]cu\d+$", arch):
        return arch
    raise RuntimeError(f"{arch} is not a supported architecture")


def _git(*args):
    """Execute a git command."""
    cwd = os.path.dirname(os.path.abspath(__file__))
    try:
        return (
            subprocess.check_output(["git", *args], stderr=subprocess.PIPE, cwd=cwd)
            .decode("ascii")
            .strip()
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return None


def parse_version(version):
    """Remove leading `v` from `version` if it matches the version convention."""
    if version is None:
        return "unknown"
    return re.sub(r"^v(\d+\.\d+\.\d+)$", r"\1", version)


def get_version_from_ref():
    """Create a version based on the git ref. Also write the version into
    ``ppl/__init__.py`` when running in the CI."""
    env_ref = os.getenv("BORCH_VERSION", os.getenv("CI_COMMIT_REF_NAME"))
    if env_ref:
        return env_ref

    tag = _git("describe", "--tags", "--exact-match")
    if tag:
        return tag

    branch = _git("symbolic-ref", "-q", "--short", "HEAD")
    if branch:
        return branch
    return None


def read_version(path):
    """Read the version listed in a given path."""
    with open(path, "rt") as f:
        return re.search(r'__version__\s*=\s*"(.+)"', f.read()).group(1)


def write_version(path):
    """Write a ``__version__`` variable into the file ``path``."""
    version = parse_version(get_version_from_ref())
    with open(path, "wt") as f:
        f.write('"""Auto-generated file -- do not edit"""\n')
        f.write(f'\n__version__ = "{version}"\n')
        return version


def read_or_write_version():
    """Either read from the version file or write a version file based on
    a git ref."""
    version_file = "src/borch/version.py"

    if os.path.isfile(version_file) and not os.getenv("DEVELOP"):
        fn = read_version
    else:
        fn = write_version

    return fn(version_file)


EXTRAS_REQUIRE = {
    "docs": [
        "matplotlib==2.2.3",
        "nbsphinx",
        "sphinx==2.2.2",
        "sphinx_gallery",
        "sphinx_rtd_theme",
        "sphinxcontrib-bibtex<2.0.0",
        "sphinx-versions==1.0.1",
        "recommonmark",
        "pillow",
        # pytorch lightening tutorial
        "pytorch_lightning",
        # graph neural networks tutorial
        "torch",
        "torchvision",
        "torch-sparse",
        "torch-geometric",
    ],
    "examples": ["notebook"],
    "lint": ["black==22.3.0", "isort==4.3.21", "pylint==2.4.4"],
    "test": ["coverage==5.2.1", "pytest-cov==2.8.1"],
}


# Install target for ALL backends
EXTRAS_REQUIRE["all-backends"] = [
    req
    for name, reqs in EXTRAS_REQUIRE.items()
    for req in reqs
    if name.startswith("backend")
]

setup(
    name="borch",
    version=read_or_write_version(),
    description="Probabilistic programming using pytorch.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Desupervised",
    license="Apache-2.0",
    url="https://gitlab.com/desupervised/borch",
    project_urls={
        "Documentaion": "https://borch.readthedocs.io/en/latest/",
        "Issues": "https://github.com/pypa/sampleproject/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    py_modules=[
        os.path.splitext(os.path.basename(path))[0] for path in glob("src/*.py")
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.17.5",
        "scipy>=1.2.0",
        "torch>=1.8.0" + get_pytorch_arch(),
    ],
    extras_require=EXTRAS_REQUIRE,
    tests_require=EXTRAS_REQUIRE["test"],
    zip_safe=True,
)
