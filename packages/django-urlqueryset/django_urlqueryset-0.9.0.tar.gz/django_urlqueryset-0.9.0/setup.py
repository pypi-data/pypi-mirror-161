import os
from setuptools import find_packages, setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_urlqueryset',
    version='0.9.0',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/MaurizioPilia/django-urlqueryset',
    install_requires=[
        'Django>=2.2',
        'djangorestframework>=3.9.4',
        'requests>=2.11.1',
        'python-magic>=0.4.18'
    ],
    extras_require={
        'test': [
            'ipython',
            'ipdb',
            'Sphinx',
            'sphinx-rtd-theme',
        ]
    },
    zip_safe=False,
)
