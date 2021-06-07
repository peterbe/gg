from os import path
from setuptools import setup, find_packages

_here = path.dirname(__file__)


dev_requirements = [
    "tox==3.14.2",
    "pytest==5.3.2",
    "pytest-mock==1.13.0",
    "pytest-cov==2.8.1",
    "pytest-sugar==0.9.2",
    "black==20.8b1",
    "flake8==3.8.3",
    "requests_mock==1.7.0",
    "therapist==2.1.0",
]

setup(
    name="gg",
    version="0.0.21",
    author="Peter Bengtsson",
    author_email="mail@peterbe.com",
    url="https://github.com/peterbe/gg",
    description="Git and GitHub for the productivity addicted",
    long_description=open(path.join(_here, "README.rst")).read(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["click", "colorama", "requests", "GitPython"],
    extras_require={"dev": dev_requirements},
    entry_points="""
        [console_scripts]
        gg=gg.main:cli
    """,
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-mock", "requests_mock"],
    keywords="git click github bugzilla",
)
