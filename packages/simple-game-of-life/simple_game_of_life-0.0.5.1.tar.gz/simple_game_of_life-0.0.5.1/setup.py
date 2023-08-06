from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="simple_game_of_life",
    version="0.0.5.1",
    py_modules=["simple_game_of_life","lexicon"],
    install_requires=["numpy", "matplotlib"],
    package_dir={"": "src"},
    description = "Conway's game of life in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
