import os

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='ckeditor5_trendig',
    version='0.6.2',
    description='CKEditor 5 for django labtrendig to s3.',
    url='https://github.com/bjvta/django_ckeditor_5/',
    author='Brandon',
    author_email='bjvtamayo78@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*example*"]),
    include_package_data=True,
    license='BSD 2-clause',
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
)