import os
from distutils.core import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-thumborstorage',
    version='0.91.2',
    license='MIT Licence',
    author='Stanislas Guerra',
    author_email='stanislas.guerra@gmail.com',
    description='Django custom storage for Thumbor backend.',
    long_description = README,
    url='https://github.com/Starou/django-thumborstorage',
    packages=['django_thumborstorage'],
    package_data={
        'django_yaaac': []
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['requests', 'mock'],
)
