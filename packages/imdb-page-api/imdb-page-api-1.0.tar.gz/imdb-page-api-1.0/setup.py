from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()


setup(
    name='imdb-page-api',
    version='1.0',
    description='A useful API to scrap movie/series/video details available on IMDb.',
    license='GNU General Public License v3.0',
    author="BlaxPanther",
    packages=["imdb-api"],
    url='https://github.com/BlaxPanther/imdb-api.git',
    keywords='python, imdb, movie-api, imdb-webscrapping, imdb-api, imdb-python, imdb-scraper',
    install_requires=install_requires,
    zip_safe=False,
    classifiers=[
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet :: WWW/HTTP',
    ]

)

