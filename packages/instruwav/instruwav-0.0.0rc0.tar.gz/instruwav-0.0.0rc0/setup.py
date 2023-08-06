import pathlib

from setuptools import find_packages, setup

this_directory = pathlib.Path(__file__).parent
with open(this_directory / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="instruwav",
    install_requires=["librosa >= 0.8.0", "pygame >= 2.0.0", "keyboardlayout >= 2.0.1", "playsound >= 1.0.1"],
    python_requires=">=3",
    version="0.0.0.pre",
    description='Generate sounds using a base note',
    author="GinoZhang",
    maintainer="Gino Zhang",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/sclass53/Instruwav",
    entry_points={
        "console_scripts": [],
    },
    license="see LICENSE.txt",
    keywords=["keyboard", "synthesizer", "instrument", "music"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    extras_require={
        "dev": [
            "setuptools",
            "wheel",
            "twine",
            "isort",
            "black",
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
