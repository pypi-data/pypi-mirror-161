from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='discontrol',
      version='0.4',
      description='Module for control discord accounts. DONT SUPORTS BOTS!',
      packages=['discontrol'],
      author_email='isgamekillerept@gmail.com',
      zip_safe=False,
      long_description=long_description,
      long_description_content_type='text/markdown')