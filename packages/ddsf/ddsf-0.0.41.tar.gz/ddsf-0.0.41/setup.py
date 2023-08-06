from setuptools import setup, find_packages

setup(
    name='ddsf',
    description='access dsf',
    version='0.0.41',
    author='Lukas Jurk',
    author_email='lukas.jurk@tu-dresden.de',
    long_description=open('readme.md').read(),
    long_description_content_type="text/markdown",
    url='https://gitlab.hrz.tu-chemnitz.de/slm/python-ddsf',
    packages=find_packages(),
    install_requires=[
        "requests",
        "pymssql"
    ],
)
