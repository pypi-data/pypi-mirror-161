from setuptools import setup, find_packages

setup(
    name='panther_config',
    url="https://panther.com",
    version='0.0.0',
    packages=find_packages(),
    package_data={'': ['bin/panther-config-darwin_amd64']},
    classifiers=[
        'Development Status :: 1 - Planning',
    ]
)
