import pathlib

from setuptools import setup

requires = [
    "flake8 > 3.0.0",
]

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="flake-type-annotations-plugin",
    description="flake8 plugin for type annotations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.1",
    license="MIT",
    author="Piotr Waszkiewicz",
    author_email="waszka23@gmail.com",
    py_modules=["flake_type_annotations_plugin"],
    package_dir={"": "src"},
    url="https://github.com/waszker/flake-type-annotations-plugin",
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="python, flake8, type annotations",
    python_requires=">=3.7, <4",
    install_requires=requires,
    entry_points={
        "flake8.extension": [
            "ANN = flake_type_annotations_plugin:TypeAnnotationsPlugin",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/waszker/flake-type-annotations-plugin/issues",
        "Source": "https://github.com/waszker/flake-type-annotations-plugin",
    },
)
