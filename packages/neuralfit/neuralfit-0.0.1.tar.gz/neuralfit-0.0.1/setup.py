from setuptools import setup, find_packages

setup(
    name='neuralfit',
    version='0.0.1',
    author="Thomas Wagenaar",
    author_email='wagenaartje@protonmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/wagenaartje/neuralfit',
    keywords=''
)