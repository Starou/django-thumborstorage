import os
from setuptools import setup

# Python 2.7
from io import open

with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    README = f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-thumborstorage',
    version='1.12.0',
    license='MIT Licence',
    author='Stanislas Guerra',
    author_email='stanislas.guerra@gmail.com',
    description='Django custom storage for Thumbor backend.',
    long_description=README,
    url='https://github.com/Starou/django-thumborstorage',
    project_urls={
        'Source Code': 'https://github.com/Starou/django-thumborstorage',
        'Issue Tracker': 'https://github.com/Starou/django-thumborstorage/issues',
    },
    install_requires=['requests', 'libthumbor'],
    packages=['django_thumborstorage'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
