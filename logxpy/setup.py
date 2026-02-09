import versioneer
from setuptools import setup


def read(path):
    """
    Read the contents of a file.
    """
    import os
    # Read from the same directory as this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)
    with open(full_path, encoding="utf-8") as f:
        return f.read()


# Read README from parent directory (project root) for markdown with images
def get_long_description():
    """Get long description from root README.md"""
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_readme = os.path.join(base_dir, "..", "README.md")
    try:
        with open(root_readme, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to package README.rst
        return read("README.rst")


setup(
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Logging",
    ],
    name="logxpy",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Modern structured logging library with hierarchical Sqid task IDs",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    python_requires=">=3.12.0",
    install_requires=[
        # Internal code documentation:
        "zope.interface",
        # Persistent objects for Python:
        "pyrsistent >= 0.11.8",  # version with multi-type pvector/pmap_field
        # Pure-Python utility library (cacheutils, dictutils, funcutils, iterutils, strutils):
        "boltons >= 24.0.0",
        # 160+ functions extending itertools (chunked, peekable, seekable, windowed, etc.):
        "more-itertools >= 10.0.0",
        # Faster JSON serialization:
        "orjson; implementation_name=='cpython'",
    ],
    extras_require={
        "journald": [
            # We use cffi to talk to the journald API:
            "cffi >= 1.1.2",  # significant API changes in older releases
        ],
        "test": [
            # Bug-seeking missile:
            "hypothesis >= 1.14.0",
            # Tasteful testing for Python:
            "testtools",
            "pytest",
            "pytest-xdist",
        ],
        "dev": [
            # Ensure we can do python_requires correctly:
            "setuptools >= 40",
            # For uploading releases:
            "twine >= 1.12.1",
            # Allows us to measure code coverage:
            "coverage",
            "sphinx",
            "sphinx_rtd_theme",
            "flake8",
            "black",
        ],
    },
    entry_points={"console_scripts": ["logxpy-prettyprint = logxpy.prettyprint:_main"]},
    keywords="logging",
    license="Apache 2.0",
    packages=["logxpy", "logxpy.tests"],
    url="https://github.com/Maziar123/log-x-py",
    maintainer="Maziar",
    maintainer_email="",
    project_urls={
        "Bug Reports": "https://github.com/Maziar123/log-x-py/issues",
        "Source": "https://github.com/Maziar123/log-x-py",
        "Documentation": "https://github.com/Maziar123/log-x-py/blob/main/README.md",
    },
)
