import os
import setuptools

with open("/home/runner/termux-1/tikapipy/README.md", "r") as fh:
    long_description = fh.read()

with open('/home/runner/termux-1/tikapipy/requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="tikapipy",
    version="1.1.3",
    author="jiroawesome",
    description="An api-wrapper for https://tiktok.jiroawesome.tech/.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jiroawesome/tikapipy",
    project_urls={
        "Bug Tracker": "https://github.com/jiroawesome/tikapipy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    package_data={'': ['**/*']},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=required
)