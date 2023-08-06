from os.path import dirname, join

from setuptools import find_packages, setup

setup(
    name='compare_for_testing',
    version='1.2.1',
    packages=find_packages(),
    author='vaindante',
    author_email='vaindante@gmail.ru',
    url='https://github.com/vaindante/compare_for_testing',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
