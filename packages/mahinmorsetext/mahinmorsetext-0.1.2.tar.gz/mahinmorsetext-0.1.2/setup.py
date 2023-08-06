from setuptools import setup, find_packages
import codecs

VERSION = '0.1.2'
DESCRIPTION = 'Morse to Text and text to morse Decoder and Encoder'
setup(
    name="mahinmorsetext",
    version=VERSION,
    author="Mahin Bin Hasan (mahinbinhasan)",
    author_email="<allmahin149@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'morsecode','morsetotext','decoder','encoder','morsedecoder'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)