import io
from os import path
from setuptools import setup, find_packages

pwd = path.abspath(path.dirname(__file__))
with io.open(path.join(pwd, 'README.md'), encoding='utf-8') as readme:
    desc = readme.read()

setup(
    name='parshu',
    version="1.0.0",
    description='Parshu uses regex to filter out the custom results. Filter URLs to save your time.',
    long_description=desc,
    long_description_content_type='text/markdown',
    author='Eshan Singh',
    author_email = 'r0x4r@yahoo.com',
    license='MIT License',
    url='https://github.com/R0X4R/Parshu',
    packages=find_packages(),
    classifiers=[
        'Topic :: Security',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords=['declutter', 'crawling', 'pentesting']
)
