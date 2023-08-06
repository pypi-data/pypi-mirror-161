from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

print(long_description)

setup(
    name='neuralfit',
    version='0.0.2',
    author="Thomas Wagenaar",
    author_email='wagenaartje@protonmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/wagenaartje/neuralfit',
    keywords='',
    long_description=long_description,
    long_description_content_type='text/markdown'
)