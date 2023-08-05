import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="testmytutor",
    version="1.0.4",
    description="test Jupyter notebook magic cell wrapper for online python tutor.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ccha23/mytutor",
    author="Chung Chan",
    license="MIT",
    classifiers=[
        "Framework :: IPython",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    packages=["testmytutor"],
    include_package_data=True,
    install_requires=[
    ],
)