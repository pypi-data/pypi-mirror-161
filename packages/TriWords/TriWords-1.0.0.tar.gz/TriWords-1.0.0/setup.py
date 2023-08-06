from setuptools import setup, find_packages

setup(
    name='TriWords',
    version='1.0.0',
    packages=find_packages(where='.', exclude=(), include=('*',)),
    include_package_data=True,
    url='https://github.com/ReddishXia/TheMainword',
    license='MIT',
    author='79988',
    author_email='77957147@qq.com',
    description='Get the main word in the paper'
)
