from setuptools import find_packages, setup
setup(
    name='formula1archive',
    packages=find_packages(include=['formula1archive']),
    version='0.2.1',
    description='Web scraping library to extract race results from F1 website',
    author='Me',
    license='MIT',
    install_requires=['pandas', 'bs4', 'plotly', 'matplotlib'],
)
