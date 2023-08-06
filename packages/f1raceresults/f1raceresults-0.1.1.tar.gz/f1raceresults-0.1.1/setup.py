from setuptools import find_packages, setup
setup(
    name='f1raceresults',
    packages=find_packages(include=['f1raceresults']),
    version='0.1.1',
    description='Web scraping library to extract race results from F1 website',
    author='Me',
    license='MIT',
    install_requires=['pandas', 'bs4', 'plotly', 'matplotlib'],
)