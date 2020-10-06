"""setup.py"""
import setuptools
from setuptools import setup

with open("README.md", "rb") as file:
    long_description = file.read().decode("utf-8")
    setup(
        name="animeX-CLI",
        license="MIT",
        packages=setuptools.find_packages(),
        description="animeX is a CLI tool for downloading anime directly to your PC",
        entry_points={
            "console_scripts": ["animex = animex.animeX:run_animeX"],
        },
        long_description=long_description,
        author="LordGhostX",
        url="https://github.com/LordGhostX/animeX-v2",
        install_requires=["wget", "requests", "beautifulsoup4"],
    )
