from pathlib import Path
from setuptools import find_packages, setup
dependencies = []
# read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name='beard-portscan',
    version='0.1.1',
    description="Simple port scanning utility at terminal forked from Aperocky/PortScan",
    author="The Bearded Tek",
    author_email="kenny@beardedtek.com",
    url="https://github.com/beardedtek/PortScan",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    project_urls={
        "Bug Tracker": "https://github.com/beardedtek/PortScan/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=dependencies,
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
)