from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='linklabs-conductor',
    version='1.6.4a7',
    description='Linklabs Conductor API Wrapper',
    long_description_content_type='text/x-rst',
    long_description=open('README.rst', encoding='utf-8').read(),
    url='https://www.link-labs.com',
    author='Linklabs, LLC',
    author_email='support@link-labs.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='linklabs symphony conductor api',
    packages=find_packages(),
    install_requires=['requests', 'python-dateutil'],
)
