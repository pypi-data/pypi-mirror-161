"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "interruptible_list", "__init__.py"), encoding="utf-8") as f:
    ast = compile(f.read(), "__init__.py", "exec")
    fake_global = {"__name__": "__main__"}
    try:
        exec(ast, fake_global)
    except (SystemError, ImportError) as e:
        print("System error")

    version = fake_global["__version__"]

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "".join(f.readlines())


setup(
    name="interruptible_list",  # Required
    version=version,  # Required
    description="Build a list from a iterable, interruptible by KeyboardInterrupt (SIGINT), and monitorable by SIGUSR1 and SIGUSR2.",  # Required
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/jb-leger/interruptible-list",  # Optional
    author="Jean-Benoist Leger",  # Optional
    author_email="jb@leger.tf",  # Optional
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    #
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    install_requires=[],  # Optional
    extras_require={},  # Optional
    package_data={},  # Optional
    data_files=[],  # Optional
    python_requires=">=3.6",
    entry_points={},  # Optional
    project_urls={},  # Optional
)
