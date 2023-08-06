from setuptools import setup, find_packages

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='password_manager_py',
    version='1.1.0',
    author="SMc",
    author_email="jackagusjill21@gmail.com",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='password manager',
    install_requires=[
        'PySimpleGUI',
        'cryptography'
    ]
)