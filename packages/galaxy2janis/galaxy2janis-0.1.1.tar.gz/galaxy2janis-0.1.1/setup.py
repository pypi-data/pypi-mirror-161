

from setuptools import setup, find_packages
from pathlib import Path

# read the contents of README.md file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
packages = ["galaxy2janis"] + ["galaxy2janis." + p for p in sorted(find_packages("./galaxy2janis"))]

setup(
    name='galaxy2janis',
    version='0.1.1',
    license='MIT',
    author='Grace Hall',
    description='ingestion of galaxy tool wrappers (.xml) and workflows (.ga) into the janis language.',
    packages=packages,
    package_data={'galaxy2janis': [
        'data/*.json',
        'data/*.yaml',
    ]},
    install_requires=[
        'galaxy-app==21.9.0',
        'janis-pipelines==0.11.6',
        'biopython==1.79',
        'filelock==3.7.0',
    ],
    entry_points={"console_scripts": ["galaxy2janis=galaxy2janis.run:main"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
)