from os import path
from setuptools import setup, find_packages

_here = path.dirname(__file__)


dev_requirements = [
    "tox==3.12.1",
    "pytest==4.6.2",
    "pytest-mock==1.10.4",
    "pytest-cov==2.7.1",
    "pytest-sugar==0.9.2",
    "black==19.3b0",
    "flake8==3.7.8",
    "requests_mock==1.6.0",
    "therapist==1.6.0",
]

setup(
    name="gg",
    version="0.0.18",
    author="Peter Bengtsson",
    author_email="mail@peterbe.com",
    url="https://github.com/peterbe/gg",
    description="Git and GitHub for the productivity addicted",
    long_description=open(path.join(_here, "README.rst")).read(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
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
