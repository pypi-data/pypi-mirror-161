from setuptools import setup, find_packages

setup(
    name='neuralfit',
    version='0.0.0',
    author="Thomas Wagenaar",
    author_email='wagenaartje@protonmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/wagenaartje/neuralfit',
    keywords='A great project is on its way!'
)